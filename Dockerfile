FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for pdfminer.six
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && apt-get clean

# Copy requirements first (for caching)
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Expose port
EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
