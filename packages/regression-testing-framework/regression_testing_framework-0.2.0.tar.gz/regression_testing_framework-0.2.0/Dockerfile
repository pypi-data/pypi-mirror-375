FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml LICENSE README.md ./
COPY src/ ./src/

# Install the package with all extras
RUN pip install --upgrade pip && \
    pip install -e .[web,monitoring]

# Create directories for data
RUN mkdir -p test_runs configs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CELERY_BROKER_URL=redis://redis:6379/0
ENV CELERY_RESULT_BACKEND=redis://redis:6379/0

# Expose ports
EXPOSE 8000 5555

# Default command
CMD ["reggie", "--help"]