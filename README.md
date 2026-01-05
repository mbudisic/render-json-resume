# Resume Forge

A CLI utility to convert JSON Resume to native PDF or DOCX documents.

## Features

- Native PDF generation using ReportLab
- Native DOCX generation using python-docx
- Multiple built-in styles (professional, modern, elegant, minimal)
- Full JSON Resume schema support
- Cross-platform (Linux, macOS, Windows)

## Installation

```bash
pip install resume-forge
```

Or install from source:

```bash
pip install -e .
```

## Usage

### Convert JSON Resume to PDF

```bash
resume-forge convert resume.json output.pdf
```

### Convert JSON Resume to DOCX

```bash
resume-forge convert resume.json output.docx
```

### Choose a style

```bash
resume-forge convert resume.json output.pdf --style modern
```

Available styles: `professional`, `modern`, `elegant`, `minimal`

### Validate a JSON Resume file

```bash
resume-forge validate resume.json
```

### List available styles

```bash
resume-forge styles
```

## JSON Resume Schema

This tool supports the full JSON Resume schema. For more information, visit:
https://jsonresume.org/schema

## License

MIT
