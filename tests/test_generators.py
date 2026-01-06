"""Tests for document generators."""

import os
import tempfile
from pathlib import Path

import pytest

from resume_forge.schema import (
    Resume, Basics, Work, Education, Skill, Profile, Location, Project,
    Certificate, Publication, Award, Volunteer, Language, Interest, Reference
)
from resume_forge.generators import PDFGenerator, DOCXGenerator
from resume_forge.generators.base import BaseGenerator


class TestBaseGenerator:
    """Test the base generator functionality."""
    
    @pytest.fixture
    def sample_resume(self) -> Resume:
        """Create a sample resume for testing."""
        return Resume(
            basics=Basics(
                name="Test Person",
                label="Software Developer",
                email="test@example.com"
            ),
            work=[
                Work(
                    name="Test Company",
                    position="Developer",
                    startDate="2020-03-15",
                    endDate="2023-06-30"
                )
            ]
        )
    
    def test_date_range_formatting_with_both_dates(self, sample_resume: Resume) -> None:
        """Date ranges should display start and end in human-readable format."""
        generator = PDFGenerator(sample_resume)
        result = generator.format_date_range("2020-03-01", "2023-06-15")
        
        assert "Mar 2020" in result
        assert "Jun 2023" in result
        assert " - " in result
    
    def test_date_range_current_job_shows_present(self, sample_resume: Resume) -> None:
        """Jobs without end date should show 'Present'."""
        generator = PDFGenerator(sample_resume)
        result = generator.format_date_range("2020-03-01", None)
        
        assert "Mar 2020" in result
        assert "Present" in result
    
    def test_date_range_empty_when_no_dates(self, sample_resume: Resume) -> None:
        """Empty date range returns empty string."""
        generator = PDFGenerator(sample_resume)
        result = generator.format_date_range(None, None)
        
        assert result == ""
    
    def test_date_formatting_handles_invalid_dates(self, sample_resume: Resume) -> None:
        """Invalid date strings should be returned as-is."""
        generator = PDFGenerator(sample_resume)
        result = generator._format_date("not-a-date")
        
        assert result == "not-a-date"
    
    def test_date_formatting_year_only(self, sample_resume: Resume) -> None:
        """Year-only dates should be returned as-is."""
        generator = PDFGenerator(sample_resume)
        result = generator._format_date("2020")
        
        assert result == "2020"


class TestPDFGenerator:
    """Test PDF document generation."""
    
    @pytest.fixture
    def comprehensive_resume(self) -> Resume:
        """Create a comprehensive resume with all sections."""
        return Resume(
            basics=Basics(
                name="John Doe",
                label="Senior Developer",
                email="john@example.com",
                phone="+1-555-1234",
                url="https://johndoe.dev",
                summary="Experienced software developer",
                location=Location(city="NYC", region="NY", countryCode="US"),
                profiles=[
                    Profile(network="GitHub", username="johndoe"),
                    Profile(network="LinkedIn", username="johndoe")
                ]
            ),
            work=[
                Work(
                    name="Tech Corp",
                    position="Senior Developer",
                    startDate="2020-01-01",
                    summary="Led development team",
                    highlights=["Built scalable systems", "Mentored juniors"]
                )
            ],
            education=[
                Education(
                    institution="MIT",
                    area="Computer Science",
                    studyType="BS",
                    startDate="2015-09-01",
                    endDate="2019-05-15"
                )
            ],
            skills=[
                Skill(name="Python", level="Expert", keywords=["Django", "FastAPI"])
            ],
            projects=[
                Project(name="Open Source Tool", url="https://github.com/test/tool")
            ]
        )
    
    def test_pdf_generation_creates_file(self, comprehensive_resume: Resume) -> None:
        """PDF generation should create an actual file."""
        generator = PDFGenerator(comprehensive_resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_pdf_contains_valid_header(self, comprehensive_resume: Resume) -> None:
        """Generated PDF should have valid PDF header."""
        generator = PDFGenerator(comprehensive_resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            with open(output_path, "rb") as pdf_file:
                header = pdf_file.read(8)
                assert header.startswith(b"%PDF")
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_all_four_styles_generate_successfully(self, comprehensive_resume: Resume) -> None:
        """All four built-in styles should generate valid PDFs."""
        styles = ["professional", "modern", "elegant", "minimal"]
        
        for style in styles:
            generator = PDFGenerator(comprehensive_resume, style=style)
            
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                output_path = Path(f.name)
            
            try:
                generator.generate(output_path)
                assert output_path.exists(), f"Style '{style}' failed to generate PDF"
                assert output_path.stat().st_size > 0
            finally:
                output_path.unlink(missing_ok=True)
    
    def test_page_size_letter_vs_a4(self, comprehensive_resume: Resume) -> None:
        """Both letter and A4 page sizes should work."""
        for page_size in ["letter", "a4"]:
            generator = PDFGenerator(comprehensive_resume, page_size=page_size)
            
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                output_path = Path(f.name)
            
            try:
                generator.generate(output_path)
                assert output_path.exists()
            finally:
                output_path.unlink(missing_ok=True)
    
    def test_empty_resume_generates_without_error(self) -> None:
        """An empty resume should still generate a valid PDF."""
        resume = Resume()
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)


class TestDOCXGenerator:
    """Test DOCX document generation."""
    
    @pytest.fixture
    def sample_resume(self) -> Resume:
        """Create a sample resume for testing."""
        return Resume(
            basics=Basics(
                name="Jane Smith",
                label="Product Manager",
                email="jane@example.com",
                summary="Strategic product leader"
            ),
            work=[
                Work(
                    name="Startup Inc",
                    position="Product Manager",
                    startDate="2021-06-01",
                    highlights=["Launched 3 products", "Grew user base 200%"]
                )
            ],
            skills=[
                Skill(name="Product Strategy", keywords=["Roadmapping", "User Research"])
            ]
        )
    
    def test_docx_generation_creates_file(self, sample_resume: Resume) -> None:
        """DOCX generation should create an actual file."""
        generator = DOCXGenerator(sample_resume)
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_docx_is_valid_zip_archive(self, sample_resume: Resume) -> None:
        """DOCX files are ZIP archives - verify the format."""
        import zipfile
        
        generator = DOCXGenerator(sample_resume)
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert zipfile.is_zipfile(output_path)
            
            with zipfile.ZipFile(output_path, "r") as zf:
                assert "word/document.xml" in zf.namelist()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_all_four_styles_generate_successfully(self, sample_resume: Resume) -> None:
        """All four built-in styles should generate valid DOCX files."""
        styles = ["professional", "modern", "elegant", "minimal"]
        
        for style in styles:
            generator = DOCXGenerator(sample_resume, style=style)
            
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
                output_path = Path(f.name)
            
            try:
                generator.generate(output_path)
                assert output_path.exists(), f"Style '{style}' failed to generate DOCX"
            finally:
                output_path.unlink(missing_ok=True)
    
    def test_empty_resume_generates_without_error(self) -> None:
        """An empty resume should still generate a valid DOCX."""
        resume = Resume()
        generator = DOCXGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)


class TestProfileURLGeneration:
    """Test automatic profile URL generation from network and username."""
    
    @pytest.fixture
    def generator(self) -> PDFGenerator:
        """Create a generator for testing."""
        resume = Resume(basics=Basics(name="Test"))
        return PDFGenerator(resume)
    
    def test_github_url_generation(self, generator: PDFGenerator) -> None:
        """GitHub profile URL should be correctly generated."""
        url = generator._get_profile_url("GitHub", "testuser")
        assert url == "https://github.com/testuser"
    
    def test_linkedin_url_generation(self, generator: PDFGenerator) -> None:
        """LinkedIn profile URL should be correctly generated."""
        url = generator._get_profile_url("LinkedIn", "testuser")
        assert url == "https://linkedin.com/in/testuser"
    
    def test_twitter_url_generation(self, generator: PDFGenerator) -> None:
        """Twitter profile URL should be correctly generated."""
        url = generator._get_profile_url("Twitter", "testuser")
        assert url == "https://twitter.com/testuser"
    
    def test_google_scholar_url_generation(self, generator: PDFGenerator) -> None:
        """Google Scholar URL should include user parameter."""
        url = generator._get_profile_url("Google Scholar", "abc123xyz")
        assert url == "https://scholar.google.com/citations?user=abc123xyz"
    
    def test_case_insensitive_network_matching(self, generator: PDFGenerator) -> None:
        """Network name matching should be case-insensitive."""
        assert generator._get_profile_url("GITHUB", "user") == "https://github.com/user"
        assert generator._get_profile_url("github", "user") == "https://github.com/user"
        assert generator._get_profile_url("GitHub", "user") == "https://github.com/user"
    
    def test_unknown_network_returns_none(self, generator: PDFGenerator) -> None:
        """Unknown networks should return None."""
        url = generator._get_profile_url("UnknownNetwork", "testuser")
        assert url is None
    
    def test_youtube_uses_at_symbol(self, generator: PDFGenerator) -> None:
        """YouTube URLs should use @ prefix for channel names."""
        url = generator._get_profile_url("YouTube", "channelname")
        assert url == "https://youtube.com/@channelname"
    
    def test_orcid_url_generation(self, generator: PDFGenerator) -> None:
        """ORCID URLs should correctly format the identifier."""
        url = generator._get_profile_url("ORCID", "0000-0002-1234-5678")
        assert url == "https://orcid.org/0000-0002-1234-5678"


class TestHyperlinkGeneration:
    """Test that hyperlinks are properly formatted."""
    
    @pytest.fixture
    def generator(self) -> PDFGenerator:
        """Create a generator for testing."""
        resume = Resume(basics=Basics(name="Test"))
        return PDFGenerator(resume)
    
    def test_make_link_creates_anchor_tag(self, generator: PDFGenerator) -> None:
        """Links should be formatted as HTML anchor tags."""
        link = generator._make_link("https://example.com", "Example")
        
        assert "<a href=" in link
        assert "https://example.com" in link
        assert ">Example</a>" in link
    
    def test_link_includes_color_attribute(self, generator: PDFGenerator) -> None:
        """Links should include a color attribute for styling."""
        link = generator._make_link("https://example.com", "Example")
        
        assert 'color="' in link


class TestGracefulMissingDates:
    """Test that generators handle missing dates gracefully without errors."""
    
    def test_work_without_dates_pdf(self) -> None:
        """Work experience without dates should generate valid PDF."""
        resume = Resume(
            basics=Basics(name="Test User"),
            work=[
                Work(name="Company A", position="Developer"),
                Work(name="Company B", position="Manager", startDate="2020-01"),
                Work(name="Company C", position="Lead", endDate="2023-12"),
            ]
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_work_without_dates_docx(self) -> None:
        """Work experience without dates should generate valid DOCX."""
        resume = Resume(
            basics=Basics(name="Test User"),
            work=[
                Work(name="Company A", position="Developer"),
                Work(name="Company B", position="Manager", startDate="2020-01"),
            ]
        )
        generator = DOCXGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_education_without_dates_pdf(self) -> None:
        """Education without dates should generate valid PDF."""
        resume = Resume(
            basics=Basics(name="Test User"),
            education=[
                Education(institution="University A", area="CS"),
                Education(institution="University B", studyType="PhD", startDate="2018"),
            ]
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_education_without_dates_docx(self) -> None:
        """Education without dates should generate valid DOCX."""
        resume = Resume(
            basics=Basics(name="Test User"),
            education=[
                Education(institution="University A", area="CS"),
            ]
        )
        generator = DOCXGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_certificates_without_dates_pdf(self) -> None:
        """Certificates without dates should generate valid PDF."""
        resume = Resume(
            basics=Basics(name="Test User"),
            certificates=[
                Certificate(name="Cert A"),
                Certificate(name="Cert B", issuer="Org X"),
                Certificate(name="Cert C", date="2022-06"),
            ]
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_certificates_without_dates_docx(self) -> None:
        """Certificates without dates should generate valid DOCX."""
        resume = Resume(
            basics=Basics(name="Test User"),
            certificates=[
                Certificate(name="Cert A"),
                Certificate(name="Cert B", issuer="Org X"),
            ]
        )
        generator = DOCXGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_publications_without_dates_pdf(self) -> None:
        """Publications without dates should generate valid PDF."""
        resume = Resume(
            basics=Basics(name="Test User"),
            publications=[
                Publication(name="Paper A"),
                Publication(name="Paper B", publisher="Journal X"),
                Publication(name="Paper C", releaseDate="2021-03"),
            ]
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_publications_without_dates_docx(self) -> None:
        """Publications without dates should generate valid DOCX."""
        resume = Resume(
            basics=Basics(name="Test User"),
            publications=[
                Publication(name="Paper A"),
                Publication(name="Paper B", publisher="Journal X"),
            ]
        )
        generator = DOCXGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_awards_without_dates_pdf(self) -> None:
        """Awards without dates should generate valid PDF."""
        resume = Resume(
            basics=Basics(name="Test User"),
            awards=[
                Award(title="Award A"),
                Award(title="Award B", awarder="Organization"),
                Award(title="Award C", date="2020-11"),
            ]
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_volunteer_without_dates_pdf(self) -> None:
        """Volunteer work without dates should generate valid PDF."""
        resume = Resume(
            basics=Basics(name="Test User"),
            volunteer=[
                Volunteer(organization="Org A", position="Volunteer"),
                Volunteer(organization="Org B", startDate="2019-01"),
            ]
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)


class TestGracefulMissingURLs:
    """Test that generators handle missing URLs gracefully without errors."""
    
    def test_projects_without_urls_pdf(self) -> None:
        """Projects without URLs should generate valid PDF."""
        resume = Resume(
            basics=Basics(name="Test User"),
            projects=[
                Project(name="Project A"),
                Project(name="Project B", description="A cool project"),
                Project(name="Project C", url="https://example.com"),
            ]
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_projects_without_urls_docx(self) -> None:
        """Projects without URLs should generate valid DOCX."""
        resume = Resume(
            basics=Basics(name="Test User"),
            projects=[
                Project(name="Project A"),
                Project(name="Project B", description="A cool project"),
            ]
        )
        generator = DOCXGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_certificates_without_urls_pdf(self) -> None:
        """Certificates without URLs should generate valid PDF."""
        resume = Resume(
            basics=Basics(name="Test User"),
            certificates=[
                Certificate(name="Cert A", issuer="Org"),
                Certificate(name="Cert B", url="https://verify.com/cert"),
            ]
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_publications_without_urls_pdf(self) -> None:
        """Publications without URLs should generate valid PDF."""
        resume = Resume(
            basics=Basics(name="Test User"),
            publications=[
                Publication(name="Paper A", publisher="Journal"),
                Publication(name="Paper B", url="https://doi.org/paper"),
            ]
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_profiles_without_urls_use_auto_generation_pdf(self) -> None:
        """Profiles without explicit URLs should use auto-generated URLs."""
        resume = Resume(
            basics=Basics(
                name="Test User",
                profiles=[
                    Profile(network="GitHub", username="testuser"),
                    Profile(network="LinkedIn", username="testuser"),
                    Profile(network="UnknownNetwork", username="testuser"),
                ]
            )
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_profiles_without_urls_docx(self) -> None:
        """Profiles without explicit URLs should generate valid DOCX."""
        resume = Resume(
            basics=Basics(
                name="Test User",
                profiles=[
                    Profile(network="GitHub", username="testuser"),
                    Profile(network="UnknownNetwork", username="testuser"),
                ]
            )
        )
        generator = DOCXGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_basics_without_url_pdf(self) -> None:
        """Basics section without personal URL should generate valid PDF."""
        resume = Resume(
            basics=Basics(
                name="Test User",
                email="test@example.com",
                label="Developer",
            )
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_basics_without_email_pdf(self) -> None:
        """Basics section without email should generate valid PDF."""
        resume = Resume(
            basics=Basics(
                name="Test User",
                label="Developer",
                url="https://example.com",
            )
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)


class TestGracefulEmptyArrays:
    """Test that generators handle empty arrays and highlights gracefully."""
    
    def test_work_with_empty_highlights_pdf(self) -> None:
        """Work with empty highlights array should generate valid PDF."""
        resume = Resume(
            basics=Basics(name="Test User"),
            work=[
                Work(name="Company", position="Developer", highlights=[]),
            ]
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_skills_with_empty_keywords_pdf(self) -> None:
        """Skills with empty keywords array should generate valid PDF."""
        resume = Resume(
            basics=Basics(name="Test User"),
            skills=[
                Skill(name="Python", keywords=[]),
                Skill(name="JavaScript"),
            ]
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_education_with_empty_courses_pdf(self) -> None:
        """Education with empty courses array should generate valid PDF."""
        resume = Resume(
            basics=Basics(name="Test User"),
            education=[
                Education(institution="University", courses=[]),
            ]
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_interests_with_empty_keywords_pdf(self) -> None:
        """Interests with empty keywords should generate valid PDF."""
        resume = Resume(
            basics=Basics(name="Test User"),
            interests=[
                Interest(name="Reading", keywords=[]),
                Interest(name="Gaming"),
            ]
        )
        generator = PDFGenerator(resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)


class TestAllSectionsGeneration:
    """Test generating documents with all resume sections populated."""
    
    @pytest.fixture
    def complete_resume(self) -> Resume:
        """Create a resume with all sections for coverage."""
        return Resume(
            basics=Basics(
                name="Complete User",
                label="Full-Stack Developer",
                email="complete@example.com",
                phone="+1-555-0100",
                url="https://completeuser.dev",
                summary="A developer with experience in all areas.",
                location=Location(city="San Francisco", region="CA", countryCode="US"),
                profiles=[
                    Profile(network="GitHub", username="completeuser"),
                    Profile(network="LinkedIn", url="https://linkedin.com/in/completeuser"),
                ]
            ),
            work=[
                Work(
                    name="Big Tech",
                    position="Senior Engineer",
                    startDate="2020-01",
                    summary="Led engineering team",
                    highlights=["Shipped major feature", "Improved performance 50%"]
                )
            ],
            education=[
                Education(
                    institution="Stanford",
                    area="Computer Science",
                    studyType="MS",
                    startDate="2016-09",
                    endDate="2018-06",
                    courses=["Machine Learning", "Distributed Systems"]
                )
            ],
            skills=[
                Skill(name="Python", level="Expert", keywords=["Django", "FastAPI"]),
                Skill(name="JavaScript", keywords=["React", "Node.js"]),
            ],
            projects=[
                Project(
                    name="Open Source CLI",
                    description="A useful command-line tool",
                    url="https://github.com/example/cli",
                    startDate="2021-01",
                    highlights=["Built with Python", "CLI tool"]
                )
            ],
            certificates=[
                Certificate(name="AWS Solutions Architect", issuer="Amazon", date="2022-03"),
            ],
            publications=[
                Publication(
                    name="Scaling Microservices",
                    publisher="Tech Journal",
                    releaseDate="2021-06",
                    url="https://example.com/paper",
                    summary="Best practices for microservice architecture"
                )
            ],
            awards=[
                Award(title="Employee of the Year", awarder="Big Tech", date="2021-12"),
            ],
            volunteer=[
                Volunteer(
                    organization="Code for Good",
                    position="Mentor",
                    startDate="2019-01",
                    highlights=["Mentored 20+ students"]
                )
            ],
            languages=[
                Language(language="English", fluency="Native"),
                Language(language="Spanish", fluency="Intermediate"),
            ],
            interests=[
                Interest(name="Open Source", keywords=["Contributing", "Maintaining"]),
            ],
            references=[
                Reference(name="Jane Manager", reference="Excellent developer and team player."),
            ]
        )
    
    def test_all_sections_pdf(self, complete_resume: Resume) -> None:
        """Complete resume with all sections should generate valid PDF."""
        generator = PDFGenerator(complete_resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
            assert output_path.stat().st_size > 1000
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_all_sections_docx(self, complete_resume: Resume) -> None:
        """Complete resume with all sections should generate valid DOCX."""
        generator = DOCXGenerator(complete_resume)
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
            assert output_path.stat().st_size > 1000
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_all_sections_all_styles_pdf(self, complete_resume: Resume) -> None:
        """Complete resume should work with all PDF styles."""
        for style in ["professional", "modern", "elegant", "minimal"]:
            generator = PDFGenerator(complete_resume, style=style)
            
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                output_path = Path(f.name)
            
            try:
                generator.generate(output_path)
                assert output_path.exists(), f"Style '{style}' failed"
            finally:
                output_path.unlink(missing_ok=True)
