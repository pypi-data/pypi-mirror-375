"""Rate limiting and retry logic for GitHub API client."""

import asyncio
import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, TypeVar, Union

from .rate_limit_progress import get_progress_manager

logger = logging.getLogger(__name__)

T = TypeVar("T")


class FailureType(Enum):
    """Classification of different failure types for circuit breaker handling."""
    RATE_LIMIT = "rate_limit"           # Should NOT count toward circuit breaker
    NETWORK_ERROR = "network_error"     # Should count, but with higher tolerance
    REPOSITORY_ACCESS = "repository_access"  # Should NOT count (expected for some forks)
    API_ERROR = "api_error"            # Should count
    TIMEOUT = "timeout"                # Should count, but with higher tolerance


@dataclass
class CircuitBreakerConfig:
    """Enhanced configuration for circuit breaker."""
    # Standard thresholds
    base_failure_threshold: int = 5
    large_repo_failure_threshold: int = 25  # Much higher for large repos
    
    # Timeout settings
    timeout_seconds: float = 60.0
    large_repo_timeout_seconds: float = 30.0  # Faster recovery for large repos
    
    # Repository size thresholds
    large_repo_fork_threshold: int = 1000
    
    # Failure type weights (how much each failure type counts toward threshold)
    failure_weights: dict[FailureType, float] = None
    
    def __post_init__(self):
        if self.failure_weights is None:
            self.failure_weights = {
                FailureType.RATE_LIMIT: 0.0,        # Rate limits don't count
                FailureType.REPOSITORY_ACCESS: 0.1,  # Repository access barely counts
                FailureType.NETWORK_ERROR: 0.5,      # Network errors count less
                FailureType.TIMEOUT: 0.5,            # Timeouts count less  
                FailureType.API_ERROR: 1.0,          # API errors count full
            }


class RequestBatcher:
    """Batches requests to minimize rate limit impact during large operations."""

    def __init__(
        self,
        batch_size: int = 10,
        batch_delay: float = 1.0,
        adaptive_batching: bool = True,
    ):
        """Initialize request batcher.

        Args:
            batch_size: Number of requests to batch together
            batch_delay: Delay between batches in seconds
            adaptive_batching: Whether to adapt batch size based on rate limit status
        """
        self.batch_size = batch_size
        self.batch_delay = batch_delay
        self.adaptive_batching = adaptive_batching
        self.current_batch_size = batch_size
        self.consecutive_successes = 0
        self.consecutive_rate_limits = 0

    async def execute_batched_requests(
        self,
        requests: list[Callable[[], Any]],
        operation_name: str = "batched requests",
        rate_limit_handler: Union["RateLimitHandler", None] = None,
    ) -> list[Any]:
        """Execute requests in batches to minimize rate limit impact.

        Args:
            requests: List of async functions to execute
            operation_name: Name of operation for logging
            rate_limit_handler: Optional rate limit handler for individual requests

        Returns:
            List of results from all requests
        """
        if not requests:
            return []

        logger.info(f"Executing {len(requests)} requests in batches for {operation_name}")
        results = []

        # Process requests in batches
        for i in range(0, len(requests), self.current_batch_size):
            batch = requests[i:i + self.current_batch_size]
            batch_num = (i // self.current_batch_size) + 1
            total_batches = (len(requests) + self.current_batch_size - 1) // self.current_batch_size

            logger.debug(f"Processing batch {batch_num}/{total_batches} with {len(batch)} requests")

            # Execute batch concurrently
            batch_results = await self._execute_batch(
                batch, f"{operation_name} batch {batch_num}", rate_limit_handler
            )
            results.extend(batch_results)

            # Adaptive delay between batches
            if i + self.current_batch_size < len(requests):  # Not the last batch
                delay = self._calculate_batch_delay()
                if delay > 0:
                    logger.debug(f"Waiting {delay:.1f}s before next batch")
                    await asyncio.sleep(delay)

        logger.info(f"Completed {len(requests)} batched requests for {operation_name}")
        return results

    async def _execute_batch(
        self,
        batch: list[Callable[[], Any]],
        batch_name: str,
        rate_limit_handler: Union["RateLimitHandler", None],
    ) -> list[Any]:
        """Execute a single batch of requests concurrently.

        Args:
            batch: List of requests in this batch
            batch_name: Name of batch for logging
            rate_limit_handler: Optional rate limit handler

        Returns:
            List of results from batch requests
        """
        tasks = []

        for i, request in enumerate(batch):
            if rate_limit_handler:
                # Wrap each request with rate limit handling
                task = rate_limit_handler.execute_with_retry(
                    request, f"{batch_name} request {i + 1}"
                )
            else:
                task = request()
            tasks.append(task)

        try:
            # Execute all requests in batch concurrently
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Count successes and rate limit errors for adaptive batching
            successes = 0
            rate_limit_errors = 0

            for result in batch_results:
                if isinstance(result, Exception):
                    from .exceptions import GitHubRateLimitError
                    if isinstance(result, GitHubRateLimitError):
                        rate_limit_errors += 1
                    # Re-raise non-rate-limit exceptions
                    elif not isinstance(result, asyncio.TimeoutError | Exception):
                        raise result
                else:
                    successes += 1

            # Update adaptive batching metrics
            if self.adaptive_batching:
                self._update_adaptive_metrics(successes, rate_limit_errors)

            # Filter out exceptions from results (they were handled by rate limiter)
            valid_results = [r for r in batch_results if not isinstance(r, Exception)]

            logger.debug(
                f"Batch completed: {successes} successes, {rate_limit_errors} rate limits, "
                f"{len(batch) - successes - rate_limit_errors} other errors"
            )

            return valid_results

        except Exception as e:
            logger.error(f"Batch execution failed for {batch_name}: {e}")
            raise

    def _update_adaptive_metrics(self, successes: int, rate_limit_errors: int) -> None:
        """Update adaptive batching metrics and adjust batch size if needed.

        Args:
            successes: Number of successful requests in batch
            rate_limit_errors: Number of rate limit errors in batch
        """
        if rate_limit_errors > 0:
            self.consecutive_rate_limits += 1
            self.consecutive_successes = 0

            # Reduce batch size if we're hitting rate limits frequently
            if self.consecutive_rate_limits >= 2 and self.current_batch_size > 1:
                old_size = self.current_batch_size
                self.current_batch_size = max(1, self.current_batch_size // 2)
                logger.info(
                    f"Reducing batch size from {old_size} to {self.current_batch_size} "
                    f"due to rate limit hits"
                )
        else:
            self.consecutive_successes += 1
            self.consecutive_rate_limits = 0

            # Increase batch size if we're consistently successful
            if self.consecutive_successes >= 5 and self.current_batch_size < self.batch_size:
                old_size = self.current_batch_size
                self.current_batch_size = min(self.batch_size, self.current_batch_size * 2)
                logger.info(
                    f"Increasing batch size from {old_size} to {self.current_batch_size} "
                    f"due to consistent success"
                )

    def _calculate_batch_delay(self) -> float:
        """Calculate delay between batches based on current conditions.

        Returns:
            Delay in seconds
        """
        base_delay = self.batch_delay

        # Increase delay if we've been hitting rate limits
        if self.consecutive_rate_limits > 0:
            multiplier = min(4.0, 1.5 ** self.consecutive_rate_limits)
            return base_delay * multiplier

        # Decrease delay if we've been consistently successful
        if self.consecutive_successes > 10:
            return base_delay * 0.5

        return base_delay


class RateLimitHandler:
    """Handles rate limiting and retry logic for GitHub API requests."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
    ):
        """Initialize rate limit handler.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff
            max_delay: Maximum delay in seconds
            backoff_factor: Multiplier for exponential backoff
            jitter: Whether to add random jitter to delays
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

    def calculate_delay(self, attempt: int, reset_time: int | None = None) -> float:
        """Calculate delay for retry attempt.

        Args:
            attempt: Current attempt number (0-based)
            reset_time: Optional rate limit reset time (Unix timestamp)

        Returns:
            Delay in seconds
        """
        if reset_time:
            # If we have a rate limit reset time, wait until then (plus a small buffer)
            current_time = time.time()
            reset_delay = max(0, reset_time - current_time + 1)  # +1 second buffer

            # Always use reset delay if it's valid and in the future, IGNORING max_delay limit
            if reset_delay > 0:
                if reset_delay > self.max_delay:
                    logger.info(f"Rate limit reset in {reset_delay:.1f} seconds (exceeds max_delay of {self.max_delay}s), waiting for full reset time...")
                else:
                    logger.info(f"Rate limit reset in {reset_delay:.1f} seconds, waiting...")
                # Return the full reset delay regardless of max_delay restriction
                return reset_delay

        # Calculate exponential backoff delay
        delay = min(self.base_delay * (self.backoff_factor ** attempt), self.max_delay)

        # Add jitter to prevent thundering herd
        if self.jitter:
            jitter_factor = 0.5 + random.random() * 0.5  # 50-100% of calculated delay
            delay *= jitter_factor

        return delay

    async def execute_with_retry(
        self,
        func: Callable[[], Any],
        operation_name: str = "API request",
        retryable_exceptions: tuple | None = None,
    ) -> Any:
        """Execute function with retry logic and exponential backoff.

        Args:
            func: Async function to execute
            operation_name: Name of operation for logging
            retryable_exceptions: Tuple of exception types that should trigger retry

        Returns:
            Result of function execution

        Raises:
            Last exception if all retries are exhausted
        """
        if retryable_exceptions is None:
            import httpx

            from .exceptions import GitHubAPIError, GitHubRateLimitError
            retryable_exceptions = (
                GitHubRateLimitError,
                httpx.TimeoutException,
                httpx.NetworkError,
                GitHubAPIError,
            )

        last_exception = None
        attempt = 0

        while True:
            try:
                if attempt == 0:
                    logger.debug(f"Executing {operation_name} (attempt {attempt + 1})")
                else:
                    logger.debug(f"Executing {operation_name} (attempt {attempt + 1})")
                result = await func()

                if attempt > 0:
                    logger.info(f"{operation_name} succeeded after {attempt + 1} attempts")

                return result

            except retryable_exceptions as e:
                # Check if this is a non-retryable GitHubAPIError
                if self._is_non_retryable_error(e):
                    error_msg = self._get_user_friendly_error_message(e)
                    logger.error(f"Non-retryable error in {operation_name}: {error_msg}")
                    raise

                last_exception = e

                # Enhanced rate limit handling
                from .exceptions import GitHubRateLimitError
                is_rate_limit_with_reset = (
                    isinstance(e, GitHubRateLimitError) and
                    e.reset_time and
                    e.reset_time > 0
                )

                # Check if we should stop retrying
                if attempt >= self.max_retries and not is_rate_limit_with_reset:
                    error_msg = self._get_user_friendly_error_message(e)
                    logger.error(f"Max retries ({self.max_retries}) exceeded for {operation_name}: {error_msg}")
                    break
                elif attempt >= self.max_retries and is_rate_limit_with_reset:
                    logger.info(f"Max retries reached but continuing for rate limit with reset time: {e.reset_time}")
                    # Continue retrying indefinitely when we have a reset time

                # Calculate delay based on exception type
                delay = self._get_delay_for_exception(e, attempt)

                # Handle rate limit errors with enhanced progress tracking
                if isinstance(e, GitHubRateLimitError):
                    await self._handle_rate_limit_wait(e, delay, operation_name, attempt)
                else:
                    # Non-rate-limit error, just log and sleep
                    error_msg = self._get_user_friendly_error_message(e)
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {operation_name}, "
                        f"retrying in {delay:.2f}s: {error_msg}"
                    )
                    await asyncio.sleep(delay)

                attempt += 1

            except Exception as e:
                # Non-retryable exception, re-raise immediately
                error_msg = self._get_user_friendly_error_message(e)
                logger.error(f"Non-retryable error in {operation_name}: {error_msg}")
                raise

        # All retries exhausted, raise the last exception with better error message
        final_error_msg = self._get_user_friendly_error_message(last_exception)
        logger.error(f"All retries exhausted for {operation_name}: {final_error_msg}")
        raise last_exception

    def _is_non_retryable_error(self, exception: Exception) -> bool:
        """Check if an exception should not be retried."""
        from .exceptions import (
            GitHubAPIError,
            GitHubAuthenticationError,
            GitHubNotFoundError,
        )

        # Authentication and not found errors are never retryable
        if isinstance(exception, GitHubAuthenticationError | GitHubNotFoundError):
            return True

        # For GitHubAPIError, only retry server errors (5xx)
        if isinstance(exception, GitHubAPIError) and exception.status_code and 400 <= exception.status_code < 500:
            # Don't retry client errors (4xx) except rate limits
            from .exceptions import GitHubRateLimitError
            if not isinstance(exception, GitHubRateLimitError):
                return True

        return False

    def _get_delay_for_exception(self, exception: Exception, attempt: int) -> float:
        """Get appropriate delay based on exception type."""
        from .exceptions import GitHubRateLimitError

        if isinstance(exception, GitHubRateLimitError):
            # For rate limit errors, use the reset time if available (bypasses normal limits)
            if exception.reset_time and exception.reset_time > 0:
                # Special handling for rate limit errors - always use reset time regardless of max_delay
                return self.calculate_delay(attempt, exception.reset_time)
            else:
                # No reset time available, use progressive backoff for rate limits
                # Use longer delays: 5min, 15min, 30min instead of short exponential backoff
                progressive_delays = [300, 900, 1800]  # 5min, 15min, 30min in seconds
                if attempt < len(progressive_delays):
                    delay = progressive_delays[attempt]
                    logger.info(f"Rate limit without reset time, using progressive backoff: {delay}s")
                    return delay
                else:
                    # For attempts beyond our progressive delays, use 30min
                    logger.info("Rate limit without reset time, using maximum backoff: 1800s (30min)")
                    return 1800
        else:
            # For other errors, use standard exponential backoff
            return self.calculate_delay(attempt)

    async def _handle_rate_limit_wait(
        self,
        exception: Any,
        delay: float,
        operation_name: str,
        attempt: int
    ) -> None:
        """Handle rate limit wait with enhanced progress tracking and immediate resumption.

        Args:
            exception: Rate limit exception
            delay: Calculated delay in seconds
            operation_name: Name of operation being retried
            attempt: Current attempt number
        """
        # Get progress tracker for this operation
        progress_manager = get_progress_manager()
        tracker = progress_manager.get_tracker(operation_name)

        # Show rate limit info if available
        if hasattr(exception, "remaining") and hasattr(exception, "limit"):
            await tracker.show_rate_limit_info(
                remaining=exception.remaining or 0,
                limit=exception.limit or 5000,
                reset_time=exception.reset_time
            )

        # Enhanced logging with better context
        if exception.reset_time and exception.reset_time > 0:
            import time
            current_time = time.time()
            actual_wait = max(0, exception.reset_time - current_time)
            logger.info(
                f"Rate limit hit on attempt {attempt + 1} for {operation_name}. "
                f"Waiting {actual_wait:.1f}s until reset at {exception.reset_time}. "
                f"This is a temporary limit - operation will resume automatically."
            )
        else:
            logger.info(
                f"Rate limit hit on attempt {attempt + 1} for {operation_name}. "
                f"No reset time available, using progressive backoff: {delay:.1f}s. "
                f"This is a temporary limit - operation will resume automatically."
            )

        # Track progress during the wait
        await tracker.track_rate_limit_wait(
            wait_seconds=delay,
            reset_time=exception.reset_time,
            operation_name=operation_name
        )

        # Sleep with progress tracking
        await asyncio.sleep(delay)

        # Show completion message with immediate resumption notice
        logger.info(f"Rate limit wait completed for {operation_name}. Resuming operation immediately.")
        await tracker.show_completion_message(operation_name)

        # Clean up tracker
        progress_manager.cleanup_tracker(operation_name)

    def _get_user_friendly_error_message(self, exception: Exception) -> str:
        """Get user-friendly error message that distinguishes between temporary and permanent failures.

        Args:
            exception: Exception to convert to user-friendly message

        Returns:
            User-friendly error message
        """
        from .exceptions import (
            GitHubAPIError,
            GitHubAuthenticationError,
            GitHubNotFoundError,
            GitHubRateLimitError,
        )

        if isinstance(exception, GitHubRateLimitError):
            if exception.reset_time and exception.reset_time > 0:
                import time
                wait_time = max(0, exception.reset_time - time.time())
                return (
                    f"Temporary rate limit exceeded. Will automatically retry in {wait_time:.0f} seconds. "
                    f"This is not a permanent failure."
                )
            else:
                return (
                    "Temporary rate limit exceeded without reset time. Will automatically retry with "
                    "progressive backoff. This is not a permanent failure."
                )

        elif isinstance(exception, GitHubAuthenticationError):
            return (
                "Permanent authentication failure. Please check your GitHub token. "
                "This will not be retried automatically."
            )

        elif isinstance(exception, GitHubNotFoundError):
            return (
                "Resource not found. This may be a permanent failure if the repository "
                "or resource doesn't exist, or temporary if it's a network issue."
            )

        elif isinstance(exception, GitHubAPIError):
            if exception.status_code:
                if 400 <= exception.status_code < 500:
                    return (
                        f"Client error ({exception.status_code}): {exception}. "
                        f"This is likely a permanent failure that won't be retried."
                    )
                elif exception.status_code >= 500:
                    return (
                        f"Server error ({exception.status_code}): {exception}. "
                        f"This is a temporary failure that will be retried automatically."
                    )
            return f"API error: {exception}. Retry behavior depends on the specific error type."

        else:
            return f"Unexpected error: {exception}. This may or may not be retried depending on the error type."


class CircuitBreaker:
    """Circuit breaker pattern implementation for API resilience."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type = Exception,
        config: CircuitBreakerConfig | None = None,
        repository_size: int = 0,
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit (legacy parameter)
            timeout: Time in seconds before attempting to close circuit (legacy parameter)
            expected_exception: Exception type that triggers circuit breaker
            config: Enhanced configuration for failure type handling
            repository_size: Number of forks in repository for adaptive behavior
        """
        # Use enhanced config if provided, otherwise create from legacy parameters
        if config is not None:
            self.config = config
        else:
            self.config = CircuitBreakerConfig(
                base_failure_threshold=failure_threshold,
                timeout_seconds=timeout
            )
        
        self.repository_size = repository_size
        self.expected_exception = expected_exception

        # Enhanced failure tracking
        self.weighted_failure_count = 0.0  # Use weighted count instead of simple count
        self.failure_history: list[tuple[float, FailureType]] = []  # Track failure types
        self.last_failure_time: float | None = None
        self.state = "closed"  # closed, open, half_open
        
        # Legacy compatibility
        self.failure_count = 0  # Keep for backward compatibility

    @property
    def failure_threshold(self) -> int:
        """Get adaptive failure threshold based on repository size."""
        if self.repository_size >= self.config.large_repo_fork_threshold:
            return self.config.large_repo_failure_threshold
        return self.config.base_failure_threshold
    
    @property
    def timeout(self) -> float:
        """Get adaptive timeout based on repository size."""
        if self.repository_size >= self.config.large_repo_fork_threshold:
            return self.config.large_repo_timeout_seconds
        return self.config.timeout_seconds

    def classify_failure(self, exception: Exception) -> FailureType:
        """Classify failure type based on exception."""
        import asyncio
        import httpx
        
        from .exceptions import (
            GitHubRateLimitError,
            GitHubNotFoundError,
            GitHubAuthenticationError,
            GitHubPrivateRepositoryError,
            GitHubForkAccessError,
            GitHubTimeoutError,
        )
        
        if isinstance(exception, GitHubRateLimitError):
            return FailureType.RATE_LIMIT
        elif isinstance(exception, (
            GitHubNotFoundError, 
            GitHubAuthenticationError,
            GitHubPrivateRepositoryError,
            GitHubForkAccessError
        )):
            return FailureType.REPOSITORY_ACCESS
        elif isinstance(exception, (asyncio.TimeoutError, GitHubTimeoutError)):
            return FailureType.TIMEOUT
        elif isinstance(exception, httpx.NetworkError):
            return FailureType.NETWORK_ERROR
        else:
            return FailureType.API_ERROR

    async def call(self, func: Callable[[], T], operation_name: str = "operation") -> T:
        """Execute function through circuit breaker.

        Args:
            func: Async function to execute
            operation_name: Name of operation for logging

        Returns:
            Result of function execution

        Raises:
            Exception if circuit is open or function fails
        """
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
                logger.info(f"Circuit breaker transitioning to half-open for {operation_name}")
            else:
                raise Exception(f"Circuit breaker is open for {operation_name}")

        try:
            result = await func()
            self._on_success(operation_name)
            return result

        except self.expected_exception as e:
            failure_type = self.classify_failure(e)
            self._on_failure(operation_name, failure_type)
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time > self.timeout

    def _on_success(self, operation_name: str) -> None:
        """Handle successful operation."""
        if self.state == "half_open":
            self.state = "closed"
            logger.info(f"Circuit breaker reset to closed for {operation_name}")
        
        # Reset all failure tracking
        self.failure_count = 0
        self.weighted_failure_count = 0.0
        self.failure_history.clear()

    def _on_failure(self, operation_name: str, failure_type: FailureType = FailureType.API_ERROR) -> None:
        """Handle failed operation with failure type classification."""
        # Legacy failure count for backward compatibility
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        # Enhanced weighted failure tracking
        weight = self.config.failure_weights.get(failure_type, 1.0)
        self.weighted_failure_count += weight
        
        # Track failure history for analysis
        self.failure_history.append((time.time(), failure_type))
        
        # Clean old failures (older than 5 minutes)
        cutoff_time = time.time() - 300
        self.failure_history = [
            (timestamp, ftype) for timestamp, ftype in self.failure_history
            if timestamp > cutoff_time
        ]
        
        # Recalculate weighted count from recent history
        self.weighted_failure_count = sum(
            self.config.failure_weights.get(ftype, 1.0)
            for _, ftype in self.failure_history
        )
        
        # Check if circuit should open based on weighted failures
        if self.weighted_failure_count >= self.failure_threshold:
            self.state = "open"
            
            # Enhanced logging with failure type breakdown
            failure_breakdown = {}
            for _, ftype in self.failure_history:
                failure_breakdown[ftype.value] = failure_breakdown.get(ftype.value, 0) + 1
            
            logger.warning(
                f"Circuit breaker opened for {operation_name} "
                f"after {self.weighted_failure_count:.1f} weighted failures "
                f"(threshold: {self.failure_threshold}). "
                f"Failure breakdown: {failure_breakdown}. "
                f"Repository size: {self.repository_size} forks."
            )
        else:
            # Log failure but circuit remains closed
            logger.debug(
                f"Circuit breaker failure recorded for {operation_name}: "
                f"{failure_type.value} (weight: {weight}). "
                f"Weighted count: {self.weighted_failure_count:.1f}/{self.failure_threshold}"
            )

class RepositorySizeDetector:
    """Detects repository characteristics to configure resilience parameters."""
    
    @staticmethod
    def extract_owner_repo_from_url(repo_url: str) -> tuple[str, str]:
        """Extract owner and repo name from GitHub URL."""
        # Handle various GitHub URL formats
        import re
        
        # Remove .git suffix if present
        repo_url = repo_url.rstrip('.git')
        
        # Match GitHub URL patterns
        patterns = [
            r'https://github\.com/([^/]+)/([^/]+)/?$',
            r'git@github\.com:([^/]+)/([^/]+)/?$',
            r'github\.com/([^/]+)/([^/]+)/?$',
            r'^([^/]+)/([^/]+)/?$',  # Simple owner/repo format
        ]
        
        for pattern in patterns:
            match = re.match(pattern, repo_url)
            if match:
                return match.group(1), match.group(2)
        
        raise ValueError(f"Could not extract owner/repo from URL: {repo_url}")
    
    @staticmethod
    async def detect_repository_size(github_client: 'GitHubClient', repo_url: str) -> int:
        """Detect the number of forks for a repository."""
        try:
            # Extract owner/repo from URL
            owner, repo = RepositorySizeDetector.extract_owner_repo_from_url(repo_url)
            
            # Get repository info to check fork count
            repo_info = await github_client.get_repository(owner, repo)
            fork_count = repo_info.forks_count if hasattr(repo_info, 'forks_count') else 0
            
            logger.info(f"Detected {fork_count} forks for {repo_url}")
            return fork_count
            
        except Exception as e:
            logger.warning(f"Could not detect repository size for {repo_url}: {e}")
            return 0  # Default to small repository behavior
    
    @staticmethod
    def get_recommended_config(fork_count: int) -> CircuitBreakerConfig:
        """Get recommended circuit breaker configuration based on repository size."""
        
        if fork_count >= 2000:
            # Very large repositories - very high tolerance
            logger.info(f"Configuring circuit breaker for very large repository ({fork_count} forks)")
            return CircuitBreakerConfig(
                base_failure_threshold=5,
                large_repo_failure_threshold=50,  # Very high threshold
                large_repo_fork_threshold=2000,
                timeout_seconds=60.0,
                large_repo_timeout_seconds=20.0,  # Quick recovery
            )
        elif fork_count >= 1000:
            # Large repositories - high tolerance  
            logger.info(f"Configuring circuit breaker for large repository ({fork_count} forks)")
            return CircuitBreakerConfig(
                base_failure_threshold=5,
                large_repo_failure_threshold=25,
                large_repo_fork_threshold=1000,
                timeout_seconds=60.0,
                large_repo_timeout_seconds=30.0,
            )
        elif fork_count >= 500:
            # Medium repositories - moderate tolerance
            logger.info(f"Configuring circuit breaker for medium repository ({fork_count} forks)")
            return CircuitBreakerConfig(
                base_failure_threshold=5,
                large_repo_failure_threshold=15,
                large_repo_fork_threshold=500,
                timeout_seconds=60.0,
                large_repo_timeout_seconds=45.0,
            )
        else:
            # Small repositories - standard behavior
            logger.debug(f"Using standard circuit breaker configuration for small repository ({fork_count} forks)")
            return CircuitBreakerConfig()  # Use defaults

@dataclass
class DegradationConfig:
    """Configuration for graceful degradation."""
    continue_on_circuit_open: bool = True
    circuit_open_retry_interval: float = 30.0  # Retry every 30 seconds
    max_circuit_open_retries: int = 10  # Try for 5 minutes total
    skip_failed_items: bool = True  # Skip items that consistently fail


class GracefulDegradationHandler:
    """Handles graceful degradation when circuit breaker opens."""
    
    def __init__(self, config: DegradationConfig):
        self.config = config
        self.circuit_open_start_time: float | None = None
        self.circuit_open_retry_count = 0
    
    async def handle_circuit_open(
        self,
        remaining_items: list[T],
        processor_func: Callable[[T], Any],
        circuit_breaker: CircuitBreaker,
        operation_name: str
    ) -> list[tuple[T, Any]]:
        """Handle processing when circuit breaker is open."""
        
        if not self.config.continue_on_circuit_open:
            raise Exception(f"Circuit breaker is open for {operation_name}, stopping processing")
        
        logger.warning(
            f"Circuit breaker is open for {operation_name}. "
            f"Will retry every {self.config.circuit_open_retry_interval}s for up to "
            f"{self.config.max_circuit_open_retries} attempts."
        )
        
        successful_results = []
        
        while self.circuit_open_retry_count < self.config.max_circuit_open_retries:
            # Wait for retry interval
            logger.info(f"Waiting {self.config.circuit_open_retry_interval}s before retrying circuit breaker recovery...")
            await asyncio.sleep(self.config.circuit_open_retry_interval)
            
            # Try to process remaining items one by one
            still_remaining = []
            
            for item in remaining_items:
                try:
                    # Try individual item processing
                    result = await circuit_breaker.call(
                        lambda: processor_func(item),
                        f"{operation_name}_individual_retry"
                    )
                    successful_results.append((item, result))
                    logger.debug(f"Successfully processed item during circuit breaker recovery: {item}")
                    
                except Exception as e:
                    if self.config.skip_failed_items:
                        logger.warning(f"Skipping failed item in {operation_name}: {e}")
                        # Don't add to still_remaining - effectively skip it
                    else:
                        still_remaining.append(item)
            
            remaining_items = still_remaining
            
            if not remaining_items:
                logger.info(f"All remaining items processed successfully for {operation_name}")
                break
                
            self.circuit_open_retry_count += 1
            logger.info(
                f"Circuit breaker retry {self.circuit_open_retry_count}/{self.config.max_circuit_open_retries} "
                f"for {operation_name}. {len(remaining_items)} items still pending."
            )
        
        if remaining_items:
            logger.warning(
                f"Circuit breaker recovery failed for {operation_name}. "
                f"{len(remaining_items)} items could not be processed."
            )
        
        return successful_results
    
    def reset_retry_count(self) -> None:
        """Reset retry count for new operations."""
        self.circuit_open_retry_count = 0
        self.circuit_open_start_time = None