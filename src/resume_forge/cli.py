"""Command-line interface for Resume Forge."""

import json
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

import click
from pydantic import ValidationError

from .schema import Resume
from .generators import PDFGenerator, DOCXGenerator


AVAILABLE_STYLES = ["professional", "modern", "elegant", "minimal"]


def is_url(path: str) -> bool:
    """Check if the given path is an HTTP/HTTPS URL."""
    return path.startswith("http://") or path.startswith("https://")


def fetch_json_from_url(url: str) -> dict:
    """Fetch and parse JSON from a URL."""
    request = Request(url, headers={"User-Agent": "resume-forge/0.1.0"})
    try:
        with urlopen(request, timeout=30) as response:
            content = response.read().decode("utf-8")
            return json.loads(content)
    except HTTPError as e:
        raise click.ClickException(f"HTTP error fetching URL: {e.code} {e.reason}")
    except URLError as e:
        raise click.ClickException(f"Error fetching URL: {e.reason}")
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON from URL: {e}")


@click.group()
@click.version_option(version="0.1.0", prog_name="resume-forge")
def main():
    """Resume Forge - Convert JSON Resume to native PDF or DOCX.
    
    A CLI utility that generates professional resumes from JSON Resume format
    to native PDF or DOCX documents without HTML intermediaries.
    """
    pass


@main.command()
@click.argument("input_source")
@click.argument("output_file", type=click.Path(path_type=Path))
@click.option(
    "--format", "-f",
    type=click.Choice(["pdf", "docx"], case_sensitive=False),
    default=None,
    help="Output format. If not specified, inferred from output file extension.",
)
@click.option(
    "--style", "-s",
    type=click.Choice(AVAILABLE_STYLES, case_sensitive=False),
    default="professional",
    help="Resume style/theme to use.",
)
@click.option(
    "--page-size", "-p",
    type=click.Choice(["letter", "a4"], case_sensitive=False),
    default="letter",
    help="Page size for PDF output.",
)
def convert(input_source: str, output_file: Path, format: str, style: str, page_size: str):
    """Convert a JSON Resume file to PDF or DOCX.
    
    INPUT_SOURCE: Path to JSON Resume file or HTTP/HTTPS URL.
    OUTPUT_FILE: Path for the output file (PDF or DOCX).
    
    Examples:
    
        resume-forge convert resume.json resume.pdf
        
        resume-forge convert resume.json resume.docx --style modern
        
        resume-forge convert https://gist.githubusercontent.com/.../resume.json output.pdf
    """
    output_format = format
    if output_format is None:
        suffix = output_file.suffix.lower()
        if suffix == ".pdf":
            output_format = "pdf"
        elif suffix == ".docx":
            output_format = "docx"
        else:
            click.echo(
                f"Error: Cannot determine output format from extension '{suffix}'. "
                "Use --format to specify.",
                err=True,
            )
            sys.exit(1)
    
    if is_url(input_source):
        click.echo(f"Fetching resume from URL...")
        data = fetch_json_from_url(input_source)
    else:
        input_file = Path(input_source)
        if not input_file.exists():
            click.echo(f"Error: File not found: {input_source}", err=True)
            sys.exit(1)
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            click.echo(f"Error: Invalid JSON in input file: {e}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"Error reading input file: {e}", err=True)
            sys.exit(1)
    
    try:
        resume = Resume.model_validate(data)
    except ValidationError as e:
        click.echo("Error: Invalid JSON Resume format:", err=True)
        for error in e.errors():
            loc = ".".join(str(x) for x in error["loc"])
            click.echo(f"  - {loc}: {error['msg']}", err=True)
        sys.exit(1)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if output_format == "pdf":
            generator = PDFGenerator(resume, style=style, page_size=page_size)
        else:
            generator = DOCXGenerator(resume, style=style)
        
        generator.generate(output_file)
        click.echo(f"Successfully generated {output_file}")
    except Exception as e:
        click.echo(f"Error generating {output_format.upper()}: {e}", err=True)
        sys.exit(1)


@main.command()
def styles():
    """List available resume styles."""
    click.echo("Available styles:")
    click.echo()
    
    style_descriptions = {
        "professional": "Clean and traditional - ideal for corporate roles",
        "modern": "Bold colors and contemporary layout - for creative industries",
        "elegant": "Refined typography with subtle accents - for executive positions",
        "minimal": "Simple black and white - maximum readability",
    }
    
    for style in AVAILABLE_STYLES:
        description = style_descriptions.get(style, "")
        click.echo(f"  {style:15} - {description}")


@main.command()
def schema():
    """Show JSON Resume schema information."""
    click.echo("JSON Resume Schema")
    click.echo("=" * 50)
    click.echo()
    click.echo("For full schema documentation, visit:")
    click.echo("  https://jsonresume.org/schema")
    click.echo()
    click.echo("Supported sections:")
    sections = [
        ("basics", "Name, contact info, summary, and social profiles"),
        ("work", "Work experience history"),
        ("volunteer", "Volunteer experience"),
        ("education", "Educational background"),
        ("awards", "Awards and honors"),
        ("certificates", "Professional certifications"),
        ("publications", "Published works"),
        ("skills", "Technical and professional skills"),
        ("languages", "Language proficiencies"),
        ("interests", "Personal interests"),
        ("references", "Professional references"),
        ("projects", "Personal or professional projects"),
    ]
    
    for name, desc in sections:
        click.echo(f"  {name:15} - {desc}")


@main.command()
@click.argument("input_source")
def validate(input_source: str):
    """Validate a JSON Resume file.
    
    INPUT_SOURCE: Path to JSON Resume file or HTTP/HTTPS URL.
    
    Examples:
    
        resume-forge validate resume.json
        
        resume-forge validate https://gist.githubusercontent.com/.../resume.json
    """
    if is_url(input_source):
        click.echo(f"Fetching resume from URL...")
        data = fetch_json_from_url(input_source)
    else:
        input_file = Path(input_source)
        if not input_file.exists():
            click.echo(f"Error: File not found: {input_source}", err=True)
            sys.exit(1)
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            click.echo(f"Error: Invalid JSON: {e}", err=True)
            sys.exit(1)
    
    try:
        resume = Resume.model_validate(data)
        click.echo(f"Valid JSON Resume: {input_source}")
        
        sections = []
        if resume.basics:
            sections.append("basics")
        if resume.work:
            sections.append(f"work ({len(resume.work)} entries)")
        if resume.education:
            sections.append(f"education ({len(resume.education)} entries)")
        if resume.skills:
            sections.append(f"skills ({len(resume.skills)} entries)")
        if resume.projects:
            sections.append(f"projects ({len(resume.projects)} entries)")
        if resume.certificates:
            sections.append(f"certificates ({len(resume.certificates)} entries)")
        if resume.awards:
            sections.append(f"awards ({len(resume.awards)} entries)")
        if resume.publications:
            sections.append(f"publications ({len(resume.publications)} entries)")
        if resume.volunteer:
            sections.append(f"volunteer ({len(resume.volunteer)} entries)")
        if resume.languages:
            sections.append(f"languages ({len(resume.languages)} entries)")
        if resume.interests:
            sections.append(f"interests ({len(resume.interests)} entries)")
        if resume.references:
            sections.append(f"references ({len(resume.references)} entries)")
        
        if sections:
            click.echo("\nSections found:")
            for section in sections:
                click.echo(f"  - {section}")
    
    except ValidationError as e:
        click.echo("Invalid JSON Resume format:", err=True)
        for error in e.errors():
            loc = ".".join(str(x) for x in error["loc"])
            click.echo(f"  - {loc}: {error['msg']}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
