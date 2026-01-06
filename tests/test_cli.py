"""Tests for CLI functionality."""

import json
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from resume_forge.cli import main, is_url, fetch_json_from_url


class TestURLDetection:
    """Test URL detection functionality."""
    
    def test_http_url_detected(self) -> None:
        """HTTP URLs should be detected as URLs."""
        assert is_url("http://example.com/resume.json")
    
    def test_https_url_detected(self) -> None:
        """HTTPS URLs should be detected as URLs."""
        assert is_url("https://example.com/resume.json")
    
    def test_file_path_not_detected_as_url(self) -> None:
        """Local file paths should not be detected as URLs."""
        assert not is_url("/path/to/resume.json")
        assert not is_url("resume.json")
        assert not is_url("./resume.json")
    
    def test_relative_path_not_url(self) -> None:
        """Relative paths should not be detected as URLs."""
        assert not is_url("data/resume.json")
        assert not is_url("../resume.json")


class TestCLIConvertCommand:
    """Test the convert command."""
    
    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI runner."""
        return CliRunner()
    
    @pytest.fixture
    def sample_resume_json(self) -> dict:
        """Create sample resume JSON data."""
        return {
            "basics": {
                "name": "Test User",
                "label": "Developer",
                "email": "test@example.com"
            },
            "work": [
                {
                    "name": "Test Company",
                    "position": "Developer",
                    "startDate": "2020-01-01"
                }
            ]
        }
    
    def test_convert_json_to_pdf(self, runner: CliRunner, sample_resume_json: dict) -> None:
        """Should convert JSON Resume to PDF."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "resume.json"
            output_file = Path(tmpdir) / "resume.pdf"
            
            with open(input_file, "w") as f:
                json.dump(sample_resume_json, f)
            
            result = runner.invoke(main, ["convert", str(input_file), str(output_file)])
            
            assert result.exit_code == 0
            assert output_file.exists()
            assert "Successfully generated" in result.output
    
    def test_convert_json_to_docx(self, runner: CliRunner, sample_resume_json: dict) -> None:
        """Should convert JSON Resume to DOCX."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "resume.json"
            output_file = Path(tmpdir) / "resume.docx"
            
            with open(input_file, "w") as f:
                json.dump(sample_resume_json, f)
            
            result = runner.invoke(main, ["convert", str(input_file), str(output_file)])
            
            assert result.exit_code == 0
            assert output_file.exists()
    
    def test_convert_with_style_option(self, runner: CliRunner, sample_resume_json: dict) -> None:
        """Should accept --style option."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "resume.json"
            output_file = Path(tmpdir) / "resume.pdf"
            
            with open(input_file, "w") as f:
                json.dump(sample_resume_json, f)
            
            result = runner.invoke(
                main, 
                ["convert", str(input_file), str(output_file), "--style", "modern"]
            )
            
            assert result.exit_code == 0
    
    def test_convert_nonexistent_file_fails(self, runner: CliRunner) -> None:
        """Should fail gracefully for nonexistent input file."""
        result = runner.invoke(main, ["convert", "nonexistent.json", "output.pdf"])
        
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "error" in result.output.lower()
    
    def test_convert_invalid_json_fails(self, runner: CliRunner) -> None:
        """Should fail gracefully for invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "invalid.json"
            output_file = Path(tmpdir) / "resume.pdf"
            
            with open(input_file, "w") as f:
                f.write("{ invalid json }")
            
            result = runner.invoke(main, ["convert", str(input_file), str(output_file)])
            
            assert result.exit_code != 0
    
    def test_format_inferred_from_extension(self, runner: CliRunner, sample_resume_json: dict) -> None:
        """Output format should be inferred from file extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "resume.json"
            pdf_output = Path(tmpdir) / "resume.pdf"
            docx_output = Path(tmpdir) / "resume.docx"
            
            with open(input_file, "w") as f:
                json.dump(sample_resume_json, f)
            
            runner.invoke(main, ["convert", str(input_file), str(pdf_output)])
            assert pdf_output.exists()
            
            runner.invoke(main, ["convert", str(input_file), str(docx_output)])
            assert docx_output.exists()


class TestCLIValidateCommand:
    """Test the validate command."""
    
    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI runner."""
        return CliRunner()
    
    def test_validate_valid_resume(self, runner: CliRunner) -> None:
        """Should validate a correct JSON Resume."""
        resume_data = {
            "basics": {"name": "Valid User"},
            "work": [{"name": "Company", "position": "Role"}]
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "resume.json"
            
            with open(input_file, "w") as f:
                json.dump(resume_data, f)
            
            result = runner.invoke(main, ["validate", str(input_file)])
            
            assert result.exit_code == 0
            assert "Valid" in result.output
    
    def test_validate_shows_sections(self, runner: CliRunner) -> None:
        """Should display found sections when validating."""
        resume_data = {
            "basics": {"name": "Test"},
            "work": [{"name": "Company"}],
            "education": [{"institution": "University"}],
            "skills": [{"name": "Python"}, {"name": "Go"}]
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "resume.json"
            
            with open(input_file, "w") as f:
                json.dump(resume_data, f)
            
            result = runner.invoke(main, ["validate", str(input_file)])
            
            assert "work" in result.output.lower()
            assert "education" in result.output.lower()
            assert "skills" in result.output.lower()


class TestCLIStylesCommand:
    """Test the styles command."""
    
    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI runner."""
        return CliRunner()
    
    def test_styles_lists_all_options(self, runner: CliRunner) -> None:
        """Should list all available styles."""
        result = runner.invoke(main, ["styles"])
        
        assert result.exit_code == 0
        assert "professional" in result.output
        assert "modern" in result.output
        assert "elegant" in result.output
        assert "minimal" in result.output
    
    def test_styles_shows_descriptions(self, runner: CliRunner) -> None:
        """Should show descriptions for each style."""
        result = runner.invoke(main, ["styles"])
        
        assert "corporate" in result.output.lower() or "traditional" in result.output.lower()


class TestCLISchemaCommand:
    """Test the schema command."""
    
    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI runner."""
        return CliRunner()
    
    def test_schema_shows_documentation_url(self, runner: CliRunner) -> None:
        """Should reference JSON Resume schema documentation."""
        result = runner.invoke(main, ["schema"])
        
        assert result.exit_code == 0
        assert "jsonresume.org" in result.output
    
    def test_schema_lists_supported_sections(self, runner: CliRunner) -> None:
        """Should list all supported resume sections."""
        result = runner.invoke(main, ["schema"])
        
        expected_sections = ["basics", "work", "education", "skills", "projects"]
        for section in expected_sections:
            assert section in result.output
    
    def test_schema_lists_additional_sections(self, runner: CliRunner) -> None:
        """Should list all additional resume sections."""
        result = runner.invoke(main, ["schema"])
        
        additional_sections = ["certificates", "publications", "languages", "interests", "references"]
        for section in additional_sections:
            assert section in result.output


class TestCLIErrorHandling:
    """Test CLI error handling and edge cases."""
    
    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI runner."""
        return CliRunner()
    
    def test_convert_unsupported_format_fails(self, runner: CliRunner) -> None:
        """Should fail for unsupported output formats."""
        resume_data = {"basics": {"name": "Test"}}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "resume.json"
            output_file = Path(tmpdir) / "resume.txt"
            
            with open(input_file, "w") as f:
                json.dump(resume_data, f)
            
            result = runner.invoke(main, ["convert", str(input_file), str(output_file)])
            
            assert result.exit_code != 0
            assert "unsupported" in result.output.lower() or "format" in result.output.lower()
    
    def test_convert_invalid_style_fails(self, runner: CliRunner) -> None:
        """Should fail for invalid style option."""
        resume_data = {"basics": {"name": "Test"}}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "resume.json"
            output_file = Path(tmpdir) / "resume.pdf"
            
            with open(input_file, "w") as f:
                json.dump(resume_data, f)
            
            result = runner.invoke(
                main, 
                ["convert", str(input_file), str(output_file), "--style", "nonexistent"]
            )
            
            assert result.exit_code != 0
    
    def test_validate_invalid_json_fails(self, runner: CliRunner) -> None:
        """Should fail gracefully for malformed JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "invalid.json"
            
            with open(input_file, "w") as f:
                f.write("not valid json at all")
            
            result = runner.invoke(main, ["validate", str(input_file)])
            
            assert result.exit_code != 0
    
    def test_validate_nonexistent_file_fails(self, runner: CliRunner) -> None:
        """Should fail gracefully for nonexistent file."""
        result = runner.invoke(main, ["validate", "does_not_exist.json"])
        
        assert result.exit_code != 0
    
    def test_convert_empty_json_object_succeeds(self, runner: CliRunner) -> None:
        """Should handle empty JSON object gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "empty.json"
            output_file = Path(tmpdir) / "empty.pdf"
            
            with open(input_file, "w") as f:
                json.dump({}, f)
            
            result = runner.invoke(main, ["convert", str(input_file), str(output_file)])
            
            assert result.exit_code == 0
            assert output_file.exists()
    
    def test_convert_creates_output_directory(self, runner: CliRunner) -> None:
        """Should create output directory if it doesn't exist."""
        resume_data = {"basics": {"name": "Test"}}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "resume.json"
            output_file = Path(tmpdir) / "subdir" / "resume.pdf"
            
            with open(input_file, "w") as f:
                json.dump(resume_data, f)
            
            result = runner.invoke(main, ["convert", str(input_file), str(output_file)])
            
            assert result.exit_code == 0
            assert output_file.exists()


class TestCLIVersionAndHelp:
    """Test CLI version and help commands."""
    
    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI runner."""
        return CliRunner()
    
    def test_version_flag_shows_version(self, runner: CliRunner) -> None:
        """--version should display version number."""
        result = runner.invoke(main, ["--version"])
        
        assert result.exit_code == 0
        assert "0." in result.output or "1." in result.output
    
    def test_help_flag_shows_commands(self, runner: CliRunner) -> None:
        """--help should show available commands."""
        result = runner.invoke(main, ["--help"])
        
        assert result.exit_code == 0
        assert "convert" in result.output
        assert "validate" in result.output
        assert "styles" in result.output
    
    def test_convert_help_shows_options(self, runner: CliRunner) -> None:
        """convert --help should show available options."""
        result = runner.invoke(main, ["convert", "--help"])
        
        assert result.exit_code == 0
        assert "--style" in result.output
