# Resume Forge

## Overview
Resume Forge is a CLI utility that converts JSON Resume files to native PDF or DOCX documents without HTML intermediaries. It provides professional document generation with multiple built-in styles.

## Project Architecture

```
.
├── src/resume_forge/
│   ├── __init__.py          # Package init
│   ├── cli.py               # Click CLI interface
│   ├── schema.py            # Pydantic models for JSON Resume
│   └── generators/
│       ├── __init__.py      # Generator exports
│       ├── base.py          # Base generator class
│       ├── pdf_generator.py # ReportLab PDF generator
│       └── docx_generator.py# python-docx DOCX generator
├── sample_resume.json       # Example JSON Resume file
├── output/                  # Generated documents
├── pyproject.toml           # Project configuration
├── README.md                # User documentation
└── DEVELOPERS.md            # Developer guide and architecture
```

## Key Features
- Native PDF generation using ReportLab
- Native DOCX generation using python-docx  
- 4 built-in styles: professional, modern, elegant, minimal
- Full JSON Resume schema support
- Cross-platform (Linux, macOS, Windows)
- Minimal runtime dependencies

## Usage

```bash
# Convert to PDF
resume-forge convert resume.json output.pdf --style professional

# Convert to DOCX
resume-forge convert resume.json output.docx --style modern

# Validate JSON Resume
resume-forge validate resume.json

# List available styles
resume-forge styles
```

## Recent Changes
- 2026-01-06: Added comprehensive type annotations to all functions and methods
- 2026-01-06: Created unit test suite with 65 concept-based tests (pytest)
- 2026-01-06: Added automatic profile URL generation for 40+ social networks
- 2026-01-06: Added clickable hyperlinks to PDFs (email, URLs, profiles)
- 2026-01-06: Switched to Liberation Sans fonts for professional Helvetica-like appearance
- 2026-01-06: Added DEVELOPERS.md with code architecture documentation
- 2026-01-05: Initial implementation of Resume Forge CLI

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Test categories:
- `test_schema.py` - JSON Resume schema validation
- `test_generators.py` - PDF/DOCX document generation
- `test_cli.py` - CLI command functionality
- `test_unicode.py` - Unicode and internationalization support

## Technologies
- Python 3.11
- Click (CLI framework)
- Pydantic (JSON validation)
- ReportLab (PDF generation)
- python-docx (DOCX generation)
