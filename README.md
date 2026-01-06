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

### From pip

```bash
pip install resume-forge
```

### From source

```bash
pip install -e .
```

### Using Docker/Podman

```bash
# Build the container
podman build -t resume-forge .

# Run commands (mount current directory as /data)
podman run -v $(pwd):/data resume-forge convert resume.json output.pdf
podman run -v $(pwd):/data resume-forge convert resume.json output.docx --style modern
podman run resume-forge styles
```

### Pre-built Executables

Download standalone executables for Linux, macOS, or Windows from the [Releases](https://github.com/mbudisic/render-json-resume/releases) page. No Python installation required.

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

## Building Executables

The project includes a GitHub Actions workflow that automatically builds standalone executables for Linux, macOS, and Windows when you create a version tag:

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

Executables are attached to the GitHub Release automatically.

## License

MIT
