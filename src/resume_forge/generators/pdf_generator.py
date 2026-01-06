"""Native PDF generator using ReportLab."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
    HRFlowable,
)

from ..schema import Resume
from .base import BaseGenerator


def _find_font_via_fc(font_name: str) -> str | None:
    """Find a font file using fontconfig (fc-match)."""
    import subprocess
    try:
        result = subprocess.run(
            ["fc-match", "-f", "%{file}", font_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


def _register_unicode_fonts():
    """Register Unicode-capable fonts for proper character support."""
    fonts_to_register = {
        "LiberationSans": "Liberation Sans:style=Regular",
        "LiberationSans-Bold": "Liberation Sans:style=Bold",
        "LiberationSerif": "Liberation Serif:style=Regular",
        "LiberationSerif-Bold": "Liberation Serif:style=Bold",
        "DejaVuSans": "DejaVu Sans:style=Book",
        "DejaVuSans-Bold": "DejaVu Sans:style=Bold",
        "DejaVuSerif": "DejaVu Serif:style=Book",
        "DejaVuSerif-Bold": "DejaVu Serif:style=Bold",
    }
    
    for font_name, fc_pattern in fonts_to_register.items():
        font_path = _find_font_via_fc(fc_pattern)
        if font_path and Path(font_path).exists():
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
            except Exception:
                pass


_register_unicode_fonts()


class PDFGenerator(BaseGenerator):
    """Generate native PDF documents from JSON Resume."""
    
    STYLES = {
        "professional": {
            "primary_color": colors.HexColor("#2c3e50"),
            "secondary_color": colors.HexColor("#7f8c8d"),
            "accent_color": colors.HexColor("#3498db"),
            "font_name": "LiberationSans",
            "font_name_bold": "LiberationSans-Bold",
        },
        "modern": {
            "primary_color": colors.HexColor("#1a1a2e"),
            "secondary_color": colors.HexColor("#4a4a4a"),
            "accent_color": colors.HexColor("#e94560"),
            "font_name": "LiberationSans",
            "font_name_bold": "LiberationSans-Bold",
        },
        "elegant": {
            "primary_color": colors.HexColor("#2d3436"),
            "secondary_color": colors.HexColor("#636e72"),
            "accent_color": colors.HexColor("#6c5ce7"),
            "font_name": "LiberationSerif",
            "font_name_bold": "LiberationSerif-Bold",
        },
        "minimal": {
            "primary_color": colors.black,
            "secondary_color": colors.HexColor("#555555"),
            "accent_color": colors.HexColor("#000000"),
            "font_name": "LiberationSans",
            "font_name_bold": "LiberationSans-Bold",
        },
    }
    
    def __init__(self, resume: Resume, style: str = "professional", page_size: str = "letter"):
        super().__init__(resume, style)
        self.page_size = letter if page_size == "letter" else A4
        self.theme = self.STYLES.get(style, self.STYLES["professional"])
        self._setup_styles()
    
    def _setup_styles(self):
        """Set up paragraph styles for the document."""
        self.styles = getSampleStyleSheet()
        
        self.styles.add(ParagraphStyle(
            name="Name",
            fontName=self.theme["font_name_bold"],
            fontSize=24,
            leading=28,
            textColor=self.theme["primary_color"],
            alignment=TA_CENTER,
            spaceAfter=4,
        ))
        
        self.styles.add(ParagraphStyle(
            name="Label",
            fontName=self.theme["font_name"],
            fontSize=14,
            leading=16,
            textColor=self.theme["secondary_color"],
            alignment=TA_CENTER,
            spaceAfter=8,
        ))
        
        self.styles.add(ParagraphStyle(
            name="Contact",
            fontName=self.theme["font_name"],
            fontSize=10,
            leading=12,
            textColor=self.theme["secondary_color"],
            alignment=TA_CENTER,
            spaceAfter=12,
        ))
        
        self.styles.add(ParagraphStyle(
            name="SectionTitle",
            fontName=self.theme["font_name_bold"],
            fontSize=12,
            leading=14,
            textColor=self.theme["accent_color"],
            spaceBefore=12,
            spaceAfter=6,
            borderPadding=(0, 0, 2, 0),
        ))
        
        self.styles.add(ParagraphStyle(
            name="ItemTitle",
            fontName=self.theme["font_name_bold"],
            fontSize=11,
            leading=13,
            textColor=self.theme["primary_color"],
            spaceAfter=2,
        ))
        
        self.styles.add(ParagraphStyle(
            name="ItemSubtitle",
            fontName=self.theme["font_name"],
            fontSize=10,
            leading=12,
            textColor=self.theme["secondary_color"],
            spaceAfter=4,
        ))
        
        self.styles.add(ParagraphStyle(
            name="Body",
            fontName=self.theme["font_name"],
            fontSize=10,
            leading=12,
            textColor=self.theme["primary_color"],
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ))
        
        self.styles.add(ParagraphStyle(
            name="BulletItem",
            fontName=self.theme["font_name"],
            fontSize=10,
            leading=12,
            textColor=self.theme["primary_color"],
            leftIndent=12,
            spaceAfter=2,
        ))
    
    def generate(self, output_path: Path) -> None:
        """Generate the PDF document."""
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=self.page_size,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )
        
        story = []
        
        if self.resume.basics:
            story.extend(self._build_header())
        
        if self.resume.work:
            story.extend(self._build_work_section())
        
        if self.resume.education:
            story.extend(self._build_education_section())
        
        if self.resume.skills:
            story.extend(self._build_skills_section())
        
        if self.resume.projects:
            story.extend(self._build_projects_section())
        
        if self.resume.certificates:
            story.extend(self._build_certificates_section())
        
        if self.resume.awards:
            story.extend(self._build_awards_section())
        
        if self.resume.publications:
            story.extend(self._build_publications_section())
        
        if self.resume.volunteer:
            story.extend(self._build_volunteer_section())
        
        if self.resume.languages:
            story.extend(self._build_languages_section())
        
        if self.resume.interests:
            story.extend(self._build_interests_section())
        
        if self.resume.references:
            story.extend(self._build_references_section())
        
        doc.build(story)
    
    def _build_header(self) -> list:
        """Build the header section with name, label, and contact info."""
        elements = []
        basics = self.resume.basics
        
        if basics.name:
            elements.append(Paragraph(basics.name, self.styles["Name"]))
        
        if basics.label:
            elements.append(Paragraph(basics.label, self.styles["Label"]))
        
        contact_parts = []
        if basics.email:
            contact_parts.append(basics.email)
        if basics.phone:
            contact_parts.append(basics.phone)
        if basics.url:
            contact_parts.append(basics.url)
        if basics.location:
            loc = basics.location
            loc_parts = [p for p in [loc.city, loc.region, loc.countryCode] if p]
            if loc_parts:
                contact_parts.append(", ".join(loc_parts))
        
        if contact_parts:
            elements.append(Paragraph(" | ".join(contact_parts), self.styles["Contact"]))
        
        if basics.profiles:
            profile_parts = []
            for profile in basics.profiles:
                if profile.network and profile.username:
                    profile_parts.append(f"{profile.network}: {profile.username}")
                elif profile.url:
                    profile_parts.append(profile.url)
            if profile_parts:
                elements.append(Paragraph(" | ".join(profile_parts), self.styles["Contact"]))
        
        if basics.summary:
            elements.append(Spacer(1, 8))
            elements.append(Paragraph(basics.summary, self.styles["Body"]))
        
        elements.append(self._section_divider())
        
        return elements
    
    def _section_divider(self):
        """Create a section divider line."""
        return HRFlowable(
            width="100%",
            thickness=1,
            color=self.theme["secondary_color"],
            spaceBefore=8,
            spaceAfter=8,
        )
    
    def _build_work_section(self) -> list:
        """Build the work experience section."""
        elements = []
        elements.append(Paragraph("EXPERIENCE", self.styles["SectionTitle"]))
        
        for job in self.resume.work:
            title_parts = []
            if job.position:
                title_parts.append(job.position)
            if job.name:
                title_parts.append(f"at {job.name}")
            if title_parts:
                elements.append(Paragraph(" ".join(title_parts), self.styles["ItemTitle"]))
            
            date_range = self.format_date_range(job.startDate, job.endDate)
            if date_range:
                elements.append(Paragraph(date_range, self.styles["ItemSubtitle"]))
            
            if job.summary:
                elements.append(Paragraph(job.summary, self.styles["Body"]))
            
            if job.highlights:
                for highlight in job.highlights:
                    elements.append(Paragraph(f"• {highlight}", self.styles["BulletItem"]))
            
            elements.append(Spacer(1, 8))
        
        return elements
    
    def _build_education_section(self) -> list:
        """Build the education section."""
        elements = []
        elements.append(Paragraph("EDUCATION", self.styles["SectionTitle"]))
        
        for edu in self.resume.education:
            title_parts = []
            if edu.studyType:
                title_parts.append(edu.studyType)
            if edu.area:
                title_parts.append(f"in {edu.area}")
            if title_parts:
                elements.append(Paragraph(" ".join(title_parts), self.styles["ItemTitle"]))
            
            if edu.institution:
                subtitle = edu.institution
                if edu.score:
                    subtitle += f" | GPA: {edu.score}"
                elements.append(Paragraph(subtitle, self.styles["ItemSubtitle"]))
            
            date_range = self.format_date_range(edu.startDate, edu.endDate)
            if date_range:
                elements.append(Paragraph(date_range, self.styles["ItemSubtitle"]))
            
            if edu.courses:
                courses_text = "Courses: " + ", ".join(edu.courses)
                elements.append(Paragraph(courses_text, self.styles["Body"]))
            
            elements.append(Spacer(1, 6))
        
        return elements
    
    def _build_skills_section(self) -> list:
        """Build the skills section."""
        elements = []
        elements.append(Paragraph("SKILLS", self.styles["SectionTitle"]))
        
        for skill in self.resume.skills:
            skill_text = ""
            if skill.name:
                skill_text = f"<b>{skill.name}</b>"
                if skill.level:
                    skill_text += f" ({skill.level})"
                if skill.keywords:
                    skill_text += ": " + ", ".join(skill.keywords)
            elements.append(Paragraph(skill_text, self.styles["Body"]))
        
        elements.append(Spacer(1, 6))
        return elements
    
    def _build_projects_section(self) -> list:
        """Build the projects section."""
        elements = []
        elements.append(Paragraph("PROJECTS", self.styles["SectionTitle"]))
        
        for project in self.resume.projects:
            if project.name:
                elements.append(Paragraph(project.name, self.styles["ItemTitle"]))
            
            date_range = self.format_date_range(project.startDate, project.endDate)
            if date_range:
                elements.append(Paragraph(date_range, self.styles["ItemSubtitle"]))
            
            if project.description:
                elements.append(Paragraph(project.description, self.styles["Body"]))
            
            if project.highlights:
                for highlight in project.highlights:
                    elements.append(Paragraph(f"• {highlight}", self.styles["BulletItem"]))
            
            if project.url:
                elements.append(Paragraph(project.url, self.styles["ItemSubtitle"]))
            
            elements.append(Spacer(1, 6))
        
        return elements
    
    def _build_certificates_section(self) -> list:
        """Build the certificates section."""
        elements = []
        elements.append(Paragraph("CERTIFICATES", self.styles["SectionTitle"]))
        
        for cert in self.resume.certificates:
            if cert.name:
                elements.append(Paragraph(cert.name, self.styles["ItemTitle"]))
            
            subtitle_parts = []
            if cert.issuer:
                subtitle_parts.append(cert.issuer)
            if cert.date:
                subtitle_parts.append(self._format_date(cert.date))
            if subtitle_parts:
                elements.append(Paragraph(" | ".join(subtitle_parts), self.styles["ItemSubtitle"]))
            
            elements.append(Spacer(1, 4))
        
        return elements
    
    def _build_awards_section(self) -> list:
        """Build the awards section."""
        elements = []
        elements.append(Paragraph("AWARDS", self.styles["SectionTitle"]))
        
        for award in self.resume.awards:
            if award.title:
                elements.append(Paragraph(award.title, self.styles["ItemTitle"]))
            
            subtitle_parts = []
            if award.awarder:
                subtitle_parts.append(award.awarder)
            if award.date:
                subtitle_parts.append(self._format_date(award.date))
            if subtitle_parts:
                elements.append(Paragraph(" | ".join(subtitle_parts), self.styles["ItemSubtitle"]))
            
            if award.summary:
                elements.append(Paragraph(award.summary, self.styles["Body"]))
            
            elements.append(Spacer(1, 4))
        
        return elements
    
    def _build_publications_section(self) -> list:
        """Build the publications section."""
        elements = []
        elements.append(Paragraph("PUBLICATIONS", self.styles["SectionTitle"]))
        
        for pub in self.resume.publications:
            if pub.name:
                elements.append(Paragraph(pub.name, self.styles["ItemTitle"]))
            
            subtitle_parts = []
            if pub.publisher:
                subtitle_parts.append(pub.publisher)
            if pub.releaseDate:
                subtitle_parts.append(self._format_date(pub.releaseDate))
            if subtitle_parts:
                elements.append(Paragraph(" | ".join(subtitle_parts), self.styles["ItemSubtitle"]))
            
            if pub.summary:
                elements.append(Paragraph(pub.summary, self.styles["Body"]))
            
            elements.append(Spacer(1, 4))
        
        return elements
    
    def _build_volunteer_section(self) -> list:
        """Build the volunteer section."""
        elements = []
        elements.append(Paragraph("VOLUNTEER", self.styles["SectionTitle"]))
        
        for vol in self.resume.volunteer:
            title_parts = []
            if vol.position:
                title_parts.append(vol.position)
            if vol.organization:
                title_parts.append(f"at {vol.organization}")
            if title_parts:
                elements.append(Paragraph(" ".join(title_parts), self.styles["ItemTitle"]))
            
            date_range = self.format_date_range(vol.startDate, vol.endDate)
            if date_range:
                elements.append(Paragraph(date_range, self.styles["ItemSubtitle"]))
            
            if vol.summary:
                elements.append(Paragraph(vol.summary, self.styles["Body"]))
            
            if vol.highlights:
                for highlight in vol.highlights:
                    elements.append(Paragraph(f"• {highlight}", self.styles["BulletItem"]))
            
            elements.append(Spacer(1, 6))
        
        return elements
    
    def _build_languages_section(self) -> list:
        """Build the languages section."""
        elements = []
        elements.append(Paragraph("LANGUAGES", self.styles["SectionTitle"]))
        
        lang_texts = []
        for lang in self.resume.languages:
            if lang.language:
                text = lang.language
                if lang.fluency:
                    text += f" ({lang.fluency})"
                lang_texts.append(text)
        
        if lang_texts:
            elements.append(Paragraph(", ".join(lang_texts), self.styles["Body"]))
        
        elements.append(Spacer(1, 6))
        return elements
    
    def _build_interests_section(self) -> list:
        """Build the interests section."""
        elements = []
        elements.append(Paragraph("INTERESTS", self.styles["SectionTitle"]))
        
        for interest in self.resume.interests:
            if interest.name:
                text = f"<b>{interest.name}</b>"
                if interest.keywords:
                    text += ": " + ", ".join(interest.keywords)
                elements.append(Paragraph(text, self.styles["Body"]))
        
        elements.append(Spacer(1, 6))
        return elements
    
    def _build_references_section(self) -> list:
        """Build the references section."""
        elements = []
        elements.append(Paragraph("REFERENCES", self.styles["SectionTitle"]))
        
        for ref in self.resume.references:
            if ref.name:
                elements.append(Paragraph(ref.name, self.styles["ItemTitle"]))
            if ref.reference:
                elements.append(Paragraph(f'"{ref.reference}"', self.styles["Body"]))
            elements.append(Spacer(1, 4))
        
        return elements
