FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY distlimiter/ ./distlimiter/
COPY examples/ ./examples/
COPY tests/ ./tests/

# Install Python dependencies
RUN pip install --no-cache-dir -e .[all]

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "examples/fastapi_example.py"]
