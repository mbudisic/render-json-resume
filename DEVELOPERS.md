# Resume Forge - Developer Guide

This document provides an overview of the codebase architecture and entry points for future development.

## Project Structure

```
.
├── src/resume_forge/           # Main package
│   ├── __init__.py             # Package version
│   ├── cli.py                  # CLI entry point (Click framework)
│   ├── schema.py               # JSON Resume data models (Pydantic)
│   └── generators/             # Document generators
│       ├── __init__.py         # Exports PDFGenerator, DOCXGenerator
│       ├── base.py             # Abstract base class for generators
│       ├── pdf_generator.py    # ReportLab-based PDF generation
│       └── docx_generator.py   # python-docx-based DOCX generation
├── sample_resume.json          # Example JSON Resume for testing
├── output/                     # Generated documents (gitignored)
├── pyproject.toml              # Package configuration and dependencies
└── README.md                   # User documentation
```

## Architecture Overview

### Data Flow

```
JSON Resume File → schema.py (validation) → Generator → PDF/DOCX File
```

1. User provides a JSON Resume file
2. `schema.py` validates and parses it into Pydantic models
3. The appropriate generator (`PDFGenerator` or `DOCXGenerator`) renders the document
4. Output is written to the specified path

### Key Components

#### 1. Schema Layer (`schema.py`)

Pydantic models that mirror the JSON Resume specification (https://jsonresume.org/schema).

**Main class:** `Resume`

Contains nested models for each section:
- `Basics` - Name, contact info, summary, profiles
- `Work` - Employment history
- `Education` - Educational background
- `Skill`, `Project`, `Certificate`, `Award`, `Publication`, `Volunteer`, `Language`, `Interest`, `Reference`

All fields are optional with sensible defaults, allowing partial resumes.

**Entry point for schema changes:** Modify models here when the JSON Resume spec changes or to add custom fields.

#### 2. Generator Layer (`generators/`)

##### Base Generator (`base.py`)

Abstract base class providing:
- Common initialization (resume data, style selection)
- Date formatting utilities (`format_date_range`, `_format_date`)

All generators must implement: `generate(output_path: Path) -> None`

##### PDF Generator (`pdf_generator.py`)

Uses ReportLab's Platypus for native PDF generation.

**Key concepts:**
- `STYLES` dict: Color/font configurations for each theme
- `_setup_styles()`: Creates ReportLab ParagraphStyles
- `_build_*_section()` methods: Each returns a list of Platypus flowables
- `generate()`: Assembles all sections into a SimpleDocTemplate

**To add a new PDF style:**
1. Add entry to `STYLES` dict with colors and fonts
2. Update `AVAILABLE_STYLES` in `cli.py`

**To modify PDF layout:**
- Section builders are in `_build_*_section()` methods
- Page margins are set in `generate()` via `SimpleDocTemplate`
- Typography is controlled via `ParagraphStyle` objects in `_setup_styles()`

##### DOCX Generator (`docx_generator.py`)

Uses python-docx for native Word document generation.

**Key concepts:**
- `STYLES` dict: Color/font configurations (uses `RGBColor`)
- `_add_paragraph()`: Helper for consistent paragraph formatting
- `_build_*()` methods: Each adds content directly to `self.doc`

**To add a new DOCX style:**
1. Add entry to `STYLES` dict
2. Ensure colors use `RGBColor` from `docx.shared`

#### 3. CLI Layer (`cli.py`)

Click-based command-line interface.

**Commands:**
- `convert` - Main conversion command (JSON → PDF/DOCX)
- `validate` - Validates JSON Resume format
- `styles` - Lists available styles
- `schema` - Shows JSON Resume schema info

**To add a new command:** Use `@main.command()` decorator pattern.

**To add a new CLI option:** Add to relevant command using Click decorators.

## Adding a New Style

1. **Define colors** in both generators:
   ```python
   # In pdf_generator.py
   "mystyle": {
       "primary_color": colors.HexColor("#..."),
       "secondary_color": colors.HexColor("#..."),
       "accent_color": colors.HexColor("#..."),
       "font_name": "Helvetica",
       "font_name_bold": "Helvetica-Bold",
   }
   
   # In docx_generator.py
   "mystyle": {
       "primary_color": RGBColor(0x.., 0x.., 0x..),
       "secondary_color": RGBColor(0x.., 0x.., 0x..),
       "accent_color": RGBColor(0x.., 0x.., 0x..),
       "font_name": "Calibri",
   }
   ```

2. **Register in CLI** (`cli.py`):
   ```python
   AVAILABLE_STYLES = ["professional", "modern", "elegant", "minimal", "mystyle"]
   ```

3. **Add description** in `styles()` command.

## Adding a New Resume Section

1. **Add Pydantic model** in `schema.py`
2. **Add field to `Resume` class** in `schema.py`
3. **Implement `_build_*_section()`** in both generators
4. **Call the builder** from `generate()` in both generators

## Adding a New Output Format

1. **Create new generator** in `generators/` extending `BaseGenerator`
2. **Export from `generators/__init__.py`**
3. **Add format option** to `convert` command in `cli.py`
4. **Handle format in convert logic**

## Dependencies

| Package | Purpose |
|---------|---------|
| click | CLI framework |
| pydantic | JSON validation and data models |
| reportlab | Native PDF generation |
| python-docx | Native DOCX generation |

## Testing

Run the CLI directly:
```bash
resume-forge validate sample_resume.json
resume-forge convert sample_resume.json output.pdf --style modern
resume-forge convert sample_resume.json output.docx --style elegant
```

## Design Decisions

1. **Native generation over HTML conversion**: HTML-to-PDF produces inconsistent margins, page breaks, and typography. Direct PDF/DOCX APIs give precise control.

2. **Built-in styles over theme packages**: JSON Resume themes output HTML. Native generation requires style definitions that map to document primitives.

3. **Optional fields with defaults**: Real-world resumes vary widely. Strict validation would reject valid use cases.

4. **Separation of concerns**: Schema, generators, and CLI are independent. Generators can be used programmatically without the CLI.

## Common Modifications

| Task | File(s) to modify |
|------|-------------------|
| Change fonts | `pdf_generator.py`, `docx_generator.py` |
| Adjust margins | `generate()` in both generators |
| Change section order | `generate()` in both generators |
| Add resume section | `schema.py` + both generators |
| Change date format | `base.py` (`_format_date()`) |
| Add CLI option | `cli.py` |
