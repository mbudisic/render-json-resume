FROM python:3.11-slim

LABEL maintainer="Resume Forge"
LABEL description="CLI utility to convert JSON Resume to native PDF or DOCX"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

RUN useradd --create-home --shell /bin/bash appuser
USER appuser

WORKDIR /data

ENTRYPOINT ["resume-forge"]
CMD ["--help"]
