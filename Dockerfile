# NPQsimple Dockerfile
# Multi-arch: AMD64/ARM64 via python:3.11-slim base

FROM python:3.11-slim

# Install system dependencies
# - pdf2image requires poppler-utils
# - LaTeX image generation requires TeX Live packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        poppler-utils \
        texlive-latex-base \
        texlive-latex-extra \
        texlive-fonts-recommended \
        texlive-fonts-extra \
        texlive-science \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Default environment (overridable)
ENV HOST=0.0.0.0 \
    PORT=8050 \
    OMNIBOARD_DISABLE=1

# Improve runtime security: run as non-root user
RUN useradd -m appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8050

CMD ["python", "index.py"]
