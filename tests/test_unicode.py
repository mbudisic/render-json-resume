"""Tests for Unicode and internationalization support."""

import tempfile
from pathlib import Path

import pytest

from resume_forge.schema import Resume, Basics, Work, Location
from resume_forge.generators import PDFGenerator, DOCXGenerator


class TestUnicodeSupport:
    """Test that Unicode characters are properly handled."""
    
    @pytest.fixture
    def croatian_resume(self) -> Resume:
        """Create a resume with Croatian diacritics."""
        return Resume(
            basics=Basics(
                name="Marko Budišić",
                label="Softverski inženjer",
                summary="Iskusan programer s fokusom na čiste arhitekture i održivi kod.",
                location=Location(
                    city="Zagreb",
                    region="Hrvatska",
                    countryCode="HR"
                )
            ),
            work=[
                Work(
                    name="Tehnološka tvrtka d.o.o.",
                    position="Viši softverski inženjer",
                    startDate="2020-01-01",
                    highlights=[
                        "Razvio sustav za obradu podataka",
                        "Vodio tim od 5 članova"
                    ]
                )
            ]
        )
    
    @pytest.fixture
    def japanese_resume(self) -> Resume:
        """Create a resume with Japanese characters."""
        return Resume(
            basics=Basics(
                name="田中太郎",
                label="ソフトウェアエンジニア",
                summary="経験豊富なプログラマー"
            )
        )
    
    @pytest.fixture
    def chinese_resume(self) -> Resume:
        """Create a resume with Chinese characters."""
        return Resume(
            basics=Basics(
                name="张三",
                label="软件工程师",
                summary="有丰富经验的程序员"
            )
        )
    
    @pytest.fixture
    def arabic_resume(self) -> Resume:
        """Create a resume with Arabic characters."""
        return Resume(
            basics=Basics(
                name="أحمد محمد",
                label="مهندس برمجيات"
            )
        )
    
    @pytest.fixture
    def emoji_resume(self) -> Resume:
        """Create a resume with emoji characters."""
        return Resume(
            basics=Basics(
                name="Test User 🚀",
                label="Developer 💻",
                summary="I love coding! 🎉"
            )
        )
    
    def test_croatian_diacritics_in_pdf(self, croatian_resume: Resume) -> None:
        """PDF should be generated with Croatian diacritics without errors."""
        generator = PDFGenerator(croatian_resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_croatian_diacritics_in_docx(self, croatian_resume: Resume) -> None:
        """DOCX should be generated with Croatian diacritics without errors."""
        generator = DOCXGenerator(croatian_resume)
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_japanese_characters_in_pdf(self, japanese_resume: Resume) -> None:
        """PDF should be generated with Japanese characters without errors."""
        generator = PDFGenerator(japanese_resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_chinese_characters_in_pdf(self, chinese_resume: Resume) -> None:
        """PDF should be generated with Chinese characters without errors."""
        generator = PDFGenerator(chinese_resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_arabic_characters_in_pdf(self, arabic_resume: Resume) -> None:
        """PDF should be generated with Arabic characters without errors."""
        generator = PDFGenerator(arabic_resume)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate(output_path)
            assert output_path.exists()
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_mixed_scripts_in_resume(self) -> None:
        """Resume with mixed scripts should generate without errors."""
        resume = Resume(
            basics=Basics(
                name="John Doe / 约翰·杜",
                label="Developer / 开发者",
                summary="Bilingual developer with experience in both English and Chinese environments."
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


class TestSpecialCharacters:
    """Test handling of special characters and edge cases."""
    
    def test_ampersand_in_company_name(self) -> None:
        """Ampersands should be properly escaped in PDF."""
        resume = Resume(
            work=[
                Work(name="Smith & Jones LLC", position="Developer")
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
    
    def test_angle_brackets_without_html_tags(self) -> None:
        """Angle brackets in non-HTML contexts should be handled."""
        resume = Resume(
            basics=Basics(
                name="Test User",
                summary="Math: x > 5 and y < 10. Use &lt;tags&gt; for escaping."
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
    
    def test_quotes_in_content(self) -> None:
        """Various quote characters should be handled."""
        resume = Resume(
            basics=Basics(
                name="Test User",
                summary='He said "Hello" and she replied \'Hi\'.'
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
    
    def test_newlines_in_summary(self) -> None:
        """Newlines in content should be handled gracefully."""
        resume = Resume(
            basics=Basics(
                name="Test User",
                summary="First paragraph.\n\nSecond paragraph.\nThird line."
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
