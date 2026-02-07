FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for pdfminer.six
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && apt-get clean

# Default to a lean cloud image. For local Docker builds, pass: --build-arg PLATFORM=LOCAL
ARG PLATFORM=CLOUD

# Copy requirements first (for caching)
COPY requirements.txt .
COPY requirements-cloud.txt .

# Install python dependencies
RUN if [ "$PLATFORM" = "LOCAL" ]; then \
        pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple -r requirements.txt; \
    else \
        pip install --no-cache-dir -r requirements-cloud.txt; \
    fi

# Copy project code
COPY . .

# Expose port
EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
