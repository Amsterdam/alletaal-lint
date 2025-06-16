"""
Tests for the CLI interface.
"""

import json
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from alletaal_lint.cli import app


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_text_file():
    """Create a temporary text file for testing."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(
            "De kat zit op de mat. De hond rent in de tuin. Dit is een test voor de CLI."
        )
        return Path(f.name)


class TestCLICommands:
    """Test CLI commands."""

    def test_version_command(self, runner):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "alletaal-lint version" in result.stdout

    def test_sentence_command(self, runner):
        """Test sentence analysis command."""
        result = runner.invoke(app, ["sentence", "De kat zit op de mat."])
        assert result.exit_code == 0
        assert "Sentence Readability Analysis" in result.stdout
        assert "LiNT Score" in result.stdout
        assert "Difficulty Level" in result.stdout

    def test_sentence_command_detailed(self, runner):
        """Test sentence command with detailed flag."""
        result = runner.invoke(app, ["sentence", "De kat zit op de mat.", "--detailed"])
        assert result.exit_code == 0
        assert "Detailed Metrics" in result.stdout
        assert "Word Frequency" in result.stdout
        assert "Max Dependency Length" in result.stdout

    def test_score_command_with_text(self, runner):
        """Test score command with text option."""
        result = runner.invoke(
            app, ["score", "--text", "De kat zit op de mat. De hond rent."]
        )
        assert result.exit_code == 0
        assert "Document Readability Summary" in result.stdout

    def test_score_command_with_file(self, runner, sample_text_file):
        """Test score command with file option."""
        try:
            result = runner.invoke(app, ["score", "--file", str(sample_text_file)])
            assert result.exit_code == 0
            assert "Document Readability Summary" in result.stdout
        finally:
            sample_text_file.unlink()  # Clean up

    def test_score_command_detailed(self, runner):
        """Test score command with detailed analysis."""
        result = runner.invoke(
            app, ["score", "--text", "Eerste zin. Tweede zin.", "--detailed"]
        )
        assert result.exit_code == 0
        assert "Sentence Analysis" in result.stdout

    def test_score_command_json_output(self, runner):
        """Test score command with JSON output."""
        result = runner.invoke(
            app, ["score", "--text", "Test zin.", "--format", "json"]
        )
        assert result.exit_code == 0

        # Should be valid JSON
        try:
            data = json.loads(result.stdout)
            assert "document_score" in data
            assert "document_level" in data
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")

    def test_score_command_csv_output(self, runner):
        """Test score command with CSV output."""
        result = runner.invoke(app, ["score", "--text", "Test zin.", "--format", "csv"])
        assert result.exit_code == 0
        assert "document_score" in result.stdout  # CSV header

    def test_score_command_file_not_found(self, runner):
        """Test score command with non-existent file."""
        result = runner.invoke(app, ["score", "--file", "nonexistent.txt"])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_score_command_no_input(self, runner):
        """Test score command without text or file."""
        result = runner.invoke(app, ["score"])
        assert result.exit_code == 1
        assert "text" in result.stdout.lower() or "file" in result.stdout.lower()


class TestCLIOutputFormats:
    """Test different CLI output formats."""

    def test_json_output_format(self, runner):
        """Test JSON output format structure."""
        result = runner.invoke(
            app,
            [
                "score",
                "--text",
                "Eerste zin. Tweede zin.",
                "--format",
                "json",
                "--detailed",
            ],
        )
        assert result.exit_code == 0

        try:
            data = json.loads(result.stdout)
            required_fields = [
                "document_score",
                "document_level",
                "document_level_description",
            ]
            for field in required_fields:
                assert field in data

            if "sentences" in data:
                for sentence in data["sentences"]:
                    assert "text" in sentence
                    assert "score" in sentence
                    assert "level" in sentence
        except json.JSONDecodeError:
            pytest.fail("Invalid JSON output")

    def test_csv_output_format(self, runner):
        """Test CSV output format structure."""
        result = runner.invoke(app, ["score", "--text", "Test zin.", "--format", "csv"])
        assert result.exit_code == 0

        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 2  # Header + at least one data row

        # Check header
        header = lines[0].split(",")
        expected_fields = ["document_score", "document_level", "sentence_count"]
        for field in expected_fields:
            assert field in header

    def test_table_output_format(self, runner):
        """Test default table output format."""
        result = runner.invoke(app, ["score", "--text", "Test zin."])
        assert result.exit_code == 0
        assert "Document Readability Summary" in result.stdout
        assert "LiNT Score" in result.stdout
        assert "Difficulty Level" in result.stdout


class TestCLIFileOperations:
    """Test file input/output operations."""

    def test_output_to_file_json(self, runner):
        """Test outputting results to file in JSON format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_file = Path(f.name)

        try:
            result = runner.invoke(
                app,
                [
                    "score",
                    "--text",
                    "Test zin.",
                    "--format",
                    "json",
                    "--output",
                    str(output_file),
                ],
            )
            assert result.exit_code == 0
            assert output_file.exists()

            # Check file content
            content = output_file.read_text(encoding="utf-8")
            data = json.loads(content)
            assert "document_score" in data
        finally:
            if output_file.exists():
                output_file.unlink()

    def test_output_to_file_csv(self, runner):
        """Test outputting results to file in CSV format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            output_file = Path(f.name)

        try:
            result = runner.invoke(
                app,
                [
                    "score",
                    "--text",
                    "Test zin.",
                    "--format",
                    "csv",
                    "--output",
                    str(output_file),
                ],
            )
            assert result.exit_code == 0
            assert output_file.exists()

            # Check file content
            content = output_file.read_text(encoding="utf-8")
            assert "document_score" in content
        finally:
            if output_file.exists():
                output_file.unlink()

    def test_input_from_file_encoding(self, runner):
        """Test reading files with different encodings."""
        # Create file with Dutch text
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("Café krijgt één nieuwe eigenaar.")
            test_file = Path(f.name)

        try:
            result = runner.invoke(app, ["score", "--file", str(test_file)])
            assert result.exit_code == 0
        finally:
            test_file.unlink()


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_invalid_format_option(self, runner):
        """Test invalid format option."""
        result = runner.invoke(
            app, ["score", "--text", "Test zin.", "--format", "invalid"]
        )
        # Should use default format or show error
        assert result.exit_code in [0, 2]  # 0 for default, 2 for argument error

    def test_empty_text_input(self, runner):
        """Test empty text input."""
        result = runner.invoke(app, ["score", "--text", ""])
        # Should handle gracefully
        assert result.exit_code in [0, 1]

    def test_help_messages(self, runner):
        """Test help messages are displayed."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Dutch Text Readability Assessment" in result.stdout

        result = runner.invoke(app, ["score", "--help"])
        assert result.exit_code == 0
        assert "Score text or file for readability" in result.stdout


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    def test_cli_consistency_with_api(self, runner):
        """Test that CLI results are consistent with core API."""
        # This is a basic consistency check
        text = "De kat zit op de mat."

        result = runner.invoke(app, ["score", "--text", text, "--format", "json"])
        assert result.exit_code == 0

        try:
            data = json.loads(result.stdout)
            assert 0 <= data["document_score"] <= 100
            assert 1 <= data["document_level"] <= 4
        except (json.JSONDecodeError, KeyError):
            pytest.fail("CLI output format inconsistent with expected API structure")

    def test_multiple_sentences_processing(self, runner):
        """Test processing of multiple sentences."""
        text = "Eerste zin. Tweede zin. Derde zin. Vierde zin."

        result = runner.invoke(app, ["score", "--text", text, "--detailed"])
        assert result.exit_code == 0
        assert "4" in result.stdout  # Should show 4 sentences

    def test_server_command_help(self, runner):
        """Test server command help (without actually starting server)."""
        result = runner.invoke(app, ["server", "--help"])
        assert result.exit_code == 0
        assert "Start the FastAPI server" in result.stdout
