"""Tests for explanation formatting utilities."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from rich.table import Table

from forkscout.analysis.explanation_formatter import ExplanationFormatter
from forkscout.models.analysis import (
    CategoryType,
    CommitCategory,
    CommitExplanation,
    CommitWithExplanation,
    FormattedExplanation,
    ImpactAssessment,
    ImpactLevel,
    MainRepoValue,
)
from forkscout.models.github import Commit


class TestExplanationFormatter:
    """Test cases for ExplanationFormatter class."""

    @pytest.fixture
    def formatter(self):
        """Create a formatter instance for testing."""
        return ExplanationFormatter(use_colors=True, use_icons=True)

    @pytest.fixture
    def formatter_no_colors(self):
        """Create a formatter instance without colors or icons."""
        return ExplanationFormatter(use_colors=False, use_icons=False)

    @pytest.fixture
    def sample_commit(self):
        """Create a sample commit for testing."""
        from forkscout.models.github import User

        author = User(
            login="testuser",
            html_url="https://github.com/testuser"
        )

        return Commit(
            sha="abc123def456789012345678901234567890abcd",  # 40 chars
            message="Add user authentication",
            author=author,
            date=datetime.now(),
            files_changed=["auth.py", "models.py"],
            additions=50,
            deletions=10
        )

    @pytest.fixture
    def sample_explanation(self):
        """Create a sample explanation for testing."""
        category = CommitCategory(
            category_type=CategoryType.FEATURE,
            confidence=0.9,
            reasoning="Adds new authentication functionality"
        )

        impact = ImpactAssessment(
            impact_level=ImpactLevel.HIGH,
            change_magnitude=60.0,
            file_criticality=0.8,
            quality_factors={"test_coverage": 0.7},
            reasoning="Significant security-related changes"
        )

        return CommitExplanation(
            commit_sha="abc123def456789012345678901234567890abcd",
            category=category,
            impact_assessment=impact,
            what_changed="Added JWT-based user authentication system",
            main_repo_value=MainRepoValue.YES,
            explanation="This commit adds a comprehensive authentication system using JWT tokens.",
            is_complex=False,
            github_url="https://github.com/owner/repo/commit/abc123def456789012345678901234567890abcd"
        )

    def test_format_category_with_icon_and_color(self, formatter):
        """Test formatting category with icon and color."""
        result = formatter.format_category_with_icon(CategoryType.FEATURE)
        assert "[FEAT]" in result
        assert "Feature" in result

    def test_format_category_without_icon_and_color(self, formatter_no_colors):
        """Test formatting category without icon and color."""
        result = formatter_no_colors.format_category_with_icon(CategoryType.FEATURE)
        assert "[FEAT]" not in result
        assert result == "Feature"

    def test_format_impact_indicator_with_icon_and_color(self, formatter):
        """Test formatting impact indicator with icon and color."""
        result = formatter.format_impact_indicator(ImpactLevel.HIGH)
        assert "[HIGH]" in result
        assert "High" in result

    def test_format_impact_indicator_without_icon_and_color(self, formatter_no_colors):
        """Test formatting impact indicator without icon and color."""
        result = formatter_no_colors.format_impact_indicator(ImpactLevel.HIGH)
        assert "[HIGH]" not in result
        assert result == "High"

    def test_separate_description_from_evaluation_simple(self, formatter, sample_explanation):
        """Test separating description from evaluation for simple commit."""
        description, evaluation = formatter.separate_description_from_evaluation(sample_explanation)

        assert description == "Added JWT-based user authentication system"
        assert evaluation == "Value for main repo: YES"

    def test_separate_description_from_evaluation_complex(self, formatter, sample_explanation):
        """Test separating description from evaluation for complex commit."""
        sample_explanation.is_complex = True
        description, evaluation = formatter.separate_description_from_evaluation(sample_explanation)

        assert description == "Added JWT-based user authentication system"
        assert evaluation == "Value for main repo: YES (Complex: does multiple things)"

    def test_create_formatted_explanation(self, formatter, sample_explanation):
        """Test creating a formatted explanation."""
        github_url = "https://github.com/owner/repo/commit/abc123def456789012345678901234567890abcd"

        formatted = formatter.create_formatted_explanation(sample_explanation, github_url)

        assert isinstance(formatted, FormattedExplanation)
        assert formatted.commit_sha == "abc123def456789012345678901234567890abcd"
        assert formatted.github_url == github_url
        assert "Feature" in formatted.category_display
        assert "High" in formatted.impact_indicator
        assert formatted.description == "Added JWT-based user authentication system"
        assert formatted.evaluation == "Value for main repo: YES"
        assert not formatted.is_complex

    def test_format_commit_explanation_with_colors(self, formatter, sample_commit, sample_explanation):
        """Test formatting a complete commit explanation with colors."""
        github_url = "https://github.com/owner/repo/commit/abc123def456789012345678901234567890abcd"

        result = formatter.format_commit_explanation(sample_commit, sample_explanation, github_url)

        # Check structure - now using ASCII characters
        assert "+- Commit: abc123de" in result
        assert "Link:" in result
        assert "Description:" in result
        assert "Assessment:" in result
        assert "Category:" in result
        assert "Impact:" in result
        assert "+" in result and "-" in result

        # Check content
        assert "Added JWT-based user authentication system" in result
        assert "Value for main repo: YES" in result

    def test_format_commit_explanation_without_colors(self, formatter_no_colors, sample_commit, sample_explanation):
        """Test formatting a complete commit explanation without colors."""
        github_url = "https://github.com/owner/repo/commit/abc123def456789012345678901234567890abcd"

        result = formatter_no_colors.format_commit_explanation(sample_commit, sample_explanation, github_url)

        # Check structure (should still have basic formatting)
        assert "+- Commit: abc123de" in result
        assert "Link:" in result  # No clickable link formatting
        assert "Description:" in result
        assert "Assessment:" in result
        assert "+" in result and "-" in result

    def test_format_commit_explanation_complex_commit(self, formatter, sample_commit, sample_explanation):
        """Test formatting a complex commit explanation."""
        sample_explanation.is_complex = True
        github_url = "https://github.com/owner/repo/commit/abc123def456789012345678901234567890abcd"

        result = formatter.format_commit_explanation(sample_commit, sample_explanation, github_url)

        assert "Complex: Does multiple things" in result

    def test_format_explanation_table(self, formatter, sample_commit, sample_explanation):
        """Test formatting explanations as a table."""
        commit_with_explanation = CommitWithExplanation(
            commit=sample_commit,
            explanation=sample_explanation
        )

        table = formatter.format_explanation_table([commit_with_explanation])

        assert isinstance(table, Table)
        assert table.title == "Commit Explanations"

        # Check that columns are present
        columns = [col.header for col in table.columns]
        expected_columns = ["SHA", "Category", "Impact", "Value", "Description", "GitHub"]
        assert columns == expected_columns

    def test_format_explanation_table_with_missing_explanation(self, formatter, sample_commit):
        """Test formatting table with missing explanation."""
        commit_with_explanation = CommitWithExplanation(
            commit=sample_commit,
            explanation=None
        )

        table = formatter.format_explanation_table([commit_with_explanation])

        assert isinstance(table, Table)
        # Should handle missing explanation gracefully

    def test_format_explanation_table_multiple_commits(self, formatter):
        """Test formatting table with multiple commits."""
        # Create multiple commits and explanations
        commits_with_explanations = []

        for i in range(3):
            from forkscout.models.github import User

            author = User(
                login="testuser",
                html_url="https://github.com/testuser"
            )

            commit = Commit(
                sha=f"abc123def456789012345678901234567890abc{i}",  # 40 chars
                message=f"Test commit {i}",
                author=author,
                date=datetime.now(),
                files_changed=[f"file{i}.py"],
                additions=10,
                deletions=5
            )

            category = CommitCategory(
                category_type=CategoryType.FEATURE,
                confidence=0.8,
                reasoning=f"Test reasoning {i}"
            )

            impact = ImpactAssessment(
                impact_level=ImpactLevel.MEDIUM,
                change_magnitude=15.0,
                file_criticality=0.5,
                quality_factors={},
                reasoning=f"Test impact {i}"
            )

            explanation = CommitExplanation(
                commit_sha=f"abc123def456789012345678901234567890abc{i}",
                category=category,
                impact_assessment=impact,
                what_changed=f"Test change {i}",
                main_repo_value=MainRepoValue.YES,
                explanation=f"Test explanation {i}",
                is_complex=False,
                github_url=f"https://github.com/owner/repo/commit/abc123def456789012345678901234567890abc{i}"
            )

            commits_with_explanations.append(CommitWithExplanation(
                commit=commit,
                explanation=explanation
            ))

        table = formatter.format_explanation_table(commits_with_explanations)

        assert isinstance(table, Table)
        # Should have 3 rows of data

    def test_format_value_indicator_with_icons(self, formatter):
        """Test formatting main repo value indicators with icons."""
        yes_result = formatter._format_value_indicator(MainRepoValue.YES)
        no_result = formatter._format_value_indicator(MainRepoValue.NO)
        unclear_result = formatter._format_value_indicator(MainRepoValue.UNCLEAR)

        assert "[YES]" in yes_result
        assert "[NO]" in no_result
        assert "[UNCLEAR]" in unclear_result
        assert "YES" in yes_result
        assert "NO" in no_result
        assert "UNCLEAR" in unclear_result

    def test_format_value_indicator_without_icons(self, formatter_no_colors):
        """Test formatting main repo value indicators without icons."""
        yes_result = formatter_no_colors._format_value_indicator(MainRepoValue.YES)
        no_result = formatter_no_colors._format_value_indicator(MainRepoValue.NO)
        unclear_result = formatter_no_colors._format_value_indicator(MainRepoValue.UNCLEAR)

        assert "[YES]" not in yes_result
        assert "[NO]" not in no_result
        assert "[UNCLEAR]" not in unclear_result
        assert yes_result == "YES"
        assert no_result == "NO"
        assert unclear_result == "UNCLEAR"

    def test_category_icons_mapping(self, formatter):
        """Test that all category types have icon mappings."""
        for category_type in CategoryType:
            icon = formatter.CATEGORY_ICONS.get(category_type)
            assert icon is not None, f"Missing icon for {category_type}"

    def test_category_colors_mapping(self, formatter):
        """Test that all category types have color mappings."""
        for category_type in CategoryType:
            color = formatter.CATEGORY_COLORS.get(category_type)
            assert color is not None, f"Missing color for {category_type}"

    def test_impact_indicators_mapping(self, formatter):
        """Test that all impact levels have indicator mappings."""
        for impact_level in ImpactLevel:
            indicator = formatter.IMPACT_INDICATORS.get(impact_level)
            assert indicator is not None, f"Missing indicator for {impact_level}"

    def test_impact_colors_mapping(self, formatter):
        """Test that all impact levels have color mappings."""
        for impact_level in ImpactLevel:
            color = formatter.IMPACT_COLORS.get(impact_level)
            assert color is not None, f"Missing color for {impact_level}"

    def test_value_indicators_mapping(self, formatter):
        """Test that all main repo values have indicator mappings."""
        for value in MainRepoValue:
            indicator = formatter.VALUE_INDICATORS.get(value)
            assert indicator is not None, f"Missing indicator for {value}"

    def test_value_colors_mapping(self, formatter):
        """Test that all main repo values have color mappings."""
        for value in MainRepoValue:
            color = formatter.VALUE_COLORS.get(value)
            assert color is not None, f"Missing color for {value}"

    @patch("forklift.analysis.explanation_formatter.Console")
    def test_print_formatted_explanation(self, mock_console_class, formatter, sample_commit, sample_explanation):
        """Test printing formatted explanation to console."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        # Create new formatter to use mocked console
        formatter = ExplanationFormatter()
        github_url = "https://github.com/owner/repo/commit/abc123def456789012345678901234567890abcd"

        formatter.print_formatted_explanation(sample_commit, sample_explanation, github_url)

        # Verify console.print was called
        mock_console.print.assert_called_once()

    @patch("forklift.analysis.explanation_formatter.Console")
    def test_print_explanation_table(self, mock_console_class, formatter, sample_commit, sample_explanation):
        """Test printing explanation table to console."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        # Create new formatter to use mocked console
        formatter = ExplanationFormatter()

        commit_with_explanation = CommitWithExplanation(
            commit=sample_commit,
            explanation=sample_explanation
        )

        formatter.print_explanation_table([commit_with_explanation])

        # Verify console.print was called
        mock_console.print.assert_called_once()

    def test_ascii_only_output_formatting(self, formatter_no_colors, sample_commit, sample_explanation):
        """Test that output uses only ASCII characters and no emojis or Unicode."""
        github_url = "https://github.com/owner/repo/commit/abc123def456789012345678901234567890abcd"

        # Test commit explanation formatting
        result = formatter_no_colors.format_commit_explanation(sample_commit, sample_explanation, github_url)

        # Verify no emojis are present
        emoji_chars = ["📝", "❓", "🟢", "❔", "🚀", "🐛", "♻️", "🧪", "🔧", "⚡", "🔒",
                      "🟡", "🟠", "🔴", "✅", "❌", "⚠️", "🔗", "⚖️"]
        for emoji in emoji_chars:
            assert emoji not in result, f"Found emoji {emoji} in ASCII-only output"

        # Verify no Unicode box drawing characters are present
        unicode_chars = ["┌", "┐", "└", "┘", "├", "┤", "┬", "┴", "┼", "─", "│"]
        for char in unicode_chars:
            assert char not in result, f"Found Unicode character {char} in ASCII-only output"

        # Verify ASCII alternatives are used
        assert "+- Commit:" in result
        assert "| Link:" in result
        assert "| Description:" in result
        assert "| Assessment:" in result

        # Test category formatting
        category_result = formatter_no_colors.format_category_with_icon(CategoryType.FEATURE)
        assert category_result == "Feature"
        assert "[FEAT]" not in category_result  # No icons when use_icons=False

        # Test impact formatting
        impact_result = formatter_no_colors.format_impact_indicator(ImpactLevel.HIGH)
        assert impact_result == "High"
        assert "[HIGH]" not in impact_result  # No indicators when use_icons=False

        # Test value formatting
        value_result = formatter_no_colors._format_value_indicator(MainRepoValue.YES)
        assert value_result == "YES"
        assert "[YES]" not in value_result  # No indicators when use_icons=False

    def test_ascii_icons_when_enabled(self, formatter, sample_commit, sample_explanation):
        """Test that ASCII text labels are used instead of emojis when icons are enabled."""
        github_url = "https://github.com/owner/repo/commit/abc123def456789012345678901234567890abcd"

        # Test category formatting with ASCII icons
        category_result = formatter.format_category_with_icon(CategoryType.FEATURE)
        assert "[FEAT]" in category_result
        assert "Feature" in category_result
        assert "🚀" not in category_result  # No emoji

        # Test impact formatting with ASCII indicators
        impact_result = formatter.format_impact_indicator(ImpactLevel.HIGH)
        assert "[HIGH]" in impact_result
        assert "High" in impact_result
        assert "🟠" not in impact_result  # No emoji

        # Test value formatting with ASCII indicators
        value_result = formatter._format_value_indicator(MainRepoValue.YES)
        assert "[YES]" in value_result
        assert "YES" in value_result
        assert "✅" not in value_result  # No emoji

        # Test all category types have ASCII labels
        for category_type in CategoryType:
            result = formatter.format_category_with_icon(category_type)
            assert "[" in result and "]" in result, f"Category {category_type} should have ASCII label"

        # Test all impact levels have ASCII labels
        for impact_level in ImpactLevel:
            result = formatter.format_impact_indicator(impact_level)
            assert "[" in result and "]" in result, f"Impact {impact_level} should have ASCII label"

        # Test all value types have ASCII labels
        for value in MainRepoValue:
            result = formatter._format_value_indicator(value)
            assert "[" in result and "]" in result, f"Value {value} should have ASCII label"

    def test_no_problematic_emojis_in_output(self, formatter, sample_commit, sample_explanation):
        """Test that specific problematic emojis mentioned in requirements are not present."""
        github_url = "https://github.com/owner/repo/commit/abc123def456789012345678901234567890abcd"

        # Get all possible output from the formatter
        result = formatter.format_commit_explanation(sample_commit, sample_explanation, github_url)

        # Create table output
        commit_with_explanation = CommitWithExplanation(
            commit=sample_commit,
            explanation=sample_explanation
        )
        table = formatter.format_explanation_table([commit_with_explanation])

        # Test all category types
        category_outputs = []
        for category_type in CategoryType:
            category_outputs.append(formatter.format_category_with_icon(category_type))

        # Test all impact levels
        impact_outputs = []
        for impact_level in ImpactLevel:
            impact_outputs.append(formatter.format_impact_indicator(impact_level))

        # Test all value types
        value_outputs = []
        for value in MainRepoValue:
            value_outputs.append(formatter._format_value_indicator(value))

        # Combine all outputs to test
        all_outputs = [result] + category_outputs + impact_outputs + value_outputs

        # Specific emojis mentioned in requirements that should NOT be present
        problematic_emojis = ["📝", "❓", "🟢", "❔"]

        for output in all_outputs:
            output_str = str(output)  # Convert to string in case it's a Rich object
            for emoji in problematic_emojis:
                assert emoji not in output_str, f"Found problematic emoji {emoji} in output: {output_str[:100]}..."

    def test_simple_table_formatter_integration(self):
        """Test that simple table formatter uses ASCII characters only."""
        formatter = ExplanationFormatter(use_simple_tables=True)

        # Create sample data
        from forkscout.models.github import User

        author = User(
            login="testuser",
            html_url="https://github.com/testuser"
        )

        commit = Commit(
            sha="abc123def456789012345678901234567890abcd",
            message="Test commit",
            author=author,
            date=datetime.now(),
            files_changed=["test.py"],
            additions=10,
            deletions=5
        )

        category = CommitCategory(
            category_type=CategoryType.FEATURE,
            confidence=0.9,
            reasoning="Test reasoning"
        )

        impact = ImpactAssessment(
            impact_level=ImpactLevel.HIGH,
            change_magnitude=60.0,
            file_criticality=0.8,
            quality_factors={"test_coverage": 0.7},
            reasoning="Test impact"
        )

        explanation = CommitExplanation(
            commit_sha="abc123def456789012345678901234567890abcd",
            category=category,
            impact_assessment=impact,
            what_changed="Test change",
            main_repo_value=MainRepoValue.YES,
            explanation="Test explanation",
            is_complex=False,
            github_url="https://github.com/owner/repo/commit/abc123def456789012345678901234567890abcd"
        )

        commit_with_explanation = CommitWithExplanation(
            commit=commit,
            explanation=explanation
        )

        # Get table output
        table_output = formatter.format_explanation_table([commit_with_explanation])

        # Should be a string (simple ASCII table), not a Rich Table object
        assert isinstance(table_output, str)

        # Should use ASCII table characters
        assert "+" in table_output  # Corner/junction characters
        assert "-" in table_output  # Horizontal lines
        assert "|" in table_output  # Vertical lines

        # Should not contain Unicode box drawing characters
        unicode_chars = ["┌", "┐", "└", "┘", "├", "┤", "┬", "┴", "┼", "─", "│"]
        for char in unicode_chars:
            assert char not in table_output, f"Found Unicode character {char} in simple table output"

    def test_all_category_icons_are_ascii_text_labels(self, formatter):
        """Test that all category icons are ASCII text labels, not emojis."""
        for category_type in CategoryType:
            icon = formatter.CATEGORY_ICONS[category_type]

            # Should be wrapped in brackets
            assert icon.startswith("[") and icon.endswith("]"), f"Category icon {icon} should be wrapped in brackets"

            # Should not contain any emojis
            emoji_chars = ["📝", "❓", "🟢", "❔", "🚀", "🐛", "♻️", "🧪", "🔧", "⚡", "🔒"]
            for emoji in emoji_chars:
                assert emoji not in icon, f"Category icon {icon} contains emoji {emoji}"

            # Should be uppercase ASCII letters/numbers only (inside brackets)
            inner_text = icon[1:-1]  # Remove brackets
            assert inner_text.isupper() or inner_text.isalnum(), f"Category icon inner text {inner_text} should be uppercase ASCII"

    def test_all_impact_indicators_are_ascii_text_labels(self, formatter):
        """Test that all impact indicators are ASCII text labels, not emojis."""
        for impact_level in ImpactLevel:
            indicator = formatter.IMPACT_INDICATORS[impact_level]

            # Should be wrapped in brackets
            assert indicator.startswith("[") and indicator.endswith("]"), f"Impact indicator {indicator} should be wrapped in brackets"

            # Should not contain any emojis
            emoji_chars = ["🟢", "🟡", "🟠", "🔴", "❓", "❔"]
            for emoji in emoji_chars:
                assert emoji not in indicator, f"Impact indicator {indicator} contains emoji {emoji}"

            # Should be uppercase ASCII letters only (inside brackets)
            inner_text = indicator[1:-1]  # Remove brackets
            assert inner_text.isupper(), f"Impact indicator inner text {inner_text} should be uppercase ASCII"

    def test_all_value_indicators_are_ascii_text_labels(self, formatter):
        """Test that all value indicators are ASCII text labels, not emojis."""
        for value in MainRepoValue:
            indicator = formatter.VALUE_INDICATORS[value]

            # Should be wrapped in brackets
            assert indicator.startswith("[") and indicator.endswith("]"), f"Value indicator {indicator} should be wrapped in brackets"

            # Should not contain any emojis
            emoji_chars = ["✅", "❌", "❓", "❔", "🟢", "🔴"]
            for emoji in emoji_chars:
                assert emoji not in indicator, f"Value indicator {indicator} contains emoji {emoji}"

            # Should be uppercase ASCII letters only (inside brackets)
            inner_text = indicator[1:-1]  # Remove brackets
            assert inner_text.isupper(), f"Value indicator inner text {inner_text} should be uppercase ASCII"

    def test_strip_rich_formatting_removes_markup(self, formatter):
        """Test that _strip_rich_formatting removes Rich markup codes."""
        # Test various Rich markup patterns
        test_cases = [
            ("[bold]Test[/bold]", "Test"),
            ("[red]Error[/red]", "Error"),
            ("[bright_green]Success[/bright_green]", "Success"),
            ("[cyan][FEAT] Feature[/cyan]", "[FEAT] Feature"),
            ("Normal text", "Normal text"),
            ("[link=url]Link text[/link]", "Link text"),
            ("[bold red]Bold Red[/bold red]", "Bold Red"),
        ]

        for input_text, expected_output in test_cases:
            result = formatter._strip_rich_formatting(input_text)
            assert result == expected_output, f"Failed to strip formatting from '{input_text}', got '{result}', expected '{expected_output}'"

    def test_commit_explanation_uses_ascii_borders_only(self, formatter_no_colors, sample_commit, sample_explanation):
        """Test that commit explanation formatting uses only ASCII border characters."""
        github_url = "https://github.com/owner/repo/commit/abc123def456789012345678901234567890abcd"

        result = formatter_no_colors.format_commit_explanation(sample_commit, sample_explanation, github_url)

        # Should use ASCII characters for borders
        assert "+- Commit:" in result
        assert "| Link:" in result
        assert "| Description:" in result
        assert "| Assessment:" in result
        assert "|    Category:" in result
        assert "|    Impact:" in result

        # Should end with ASCII border
        lines = result.split("\n")
        last_line = lines[-1]
        assert last_line.startswith("+") and "-" in last_line

        # Should not contain Unicode box drawing characters
        unicode_box_chars = ["┌", "┐", "└", "┘", "├", "┤", "┬", "┴", "┼", "─", "│", "╭", "╮", "╯", "╰"]
        for char in unicode_box_chars:
            assert char not in result, f"Found Unicode box drawing character '{char}' in commit explanation output"
