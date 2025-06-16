# Multi-stage build for alletaal-lint
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY pyproject.toml .
RUN pip install --upgrade pip setuptools wheel && \
    pip install build

# Copy source code and build wheel
COPY . .
RUN python -m build --wheel && \
    pip install dist/*.whl

# Download Dutch spaCy model
RUN python -m spacy download nl_core_news_sm

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root user
RUN groupadd -r alletaal && useradd -r -g alletaal alletaal

# Create app directory and set permissions
WORKDIR /app
RUN chown alletaal:alletaal /app

# Switch to non-root user
USER alletaal

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command - start API server
CMD ["alletaal-lint", "server", "--host", "0.0.0.0", "--port", "8000"]