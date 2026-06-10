FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860

WORKDIR /app

# Install system dependencies (e.g. gettext for translating messages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gettext \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv globally
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependencies and install them system-wide
COPY requirements.txt ./
RUN uv pip install --system -r requirements.txt

# Create a non-root user with UID 1000
RUN useradd -m -u 1000 appuser

# Copy project files and set ownership
COPY --chown=appuser:appuser . .

# Switch to the non-root user
USER appuser

# Expose port 7860
EXPOSE 7860

# Execute startup script
CMD ["./start.sh"]
