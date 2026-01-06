# Resume Forge

[![Tests](https://github.com/mbudisic/render-json-resume/actions/workflows/tests.yml/badge.svg)](https://github.com/mbudisic/render-json-resume/actions/workflows/tests.yml)
![Coverage](./coverage.svg)
[![Replit](https://img.shields.io/badge/Developed%20on-Replit-F26207?logo=replit&logoColor=white)](https://replit.com)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)

A CLI utility to convert JSON Resume to native PDF or DOCX documents.

## Features

- Native PDF generation using ReportLab
- Native DOCX generation using python-docx
- Multiple built-in styles (professional, modern, elegant, minimal)
- Full JSON Resume schema support
- Cross-platform (Linux, macOS, Windows)
- Fetch resumes from HTTP/HTTPS URLs (GitHub Gist, etc.)

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

### Convert from a URL (GitHub Gist, etc.)

```bash
resume-forge convert https://gist.githubusercontent.com/user/id/raw/resume.json output.pdf
```

### Choose a style

```bash
resume-forge convert resume.json output.pdf --style modern
```

Available styles: `professional`, `modern`, `elegant`, `minimal`

### Validate a JSON Resume file

```bash
resume-forge validate resume.json

# Or validate from a URL
resume-forge validate https://gist.githubusercontent.com/.../resume.json
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
