# Use a stable Python version
FROM python:3.11-slim

# Prevent Python from writing .pyc files & buffer logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system deps (for pandas / numpy / sklearn, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY scripts ./scripts
COPY recommender.py scrape_catalog.py ./

# Copy data (just the catalog needed at runtime)
COPY data/catalog.csv ./data/catalog.csv

# Expose API port
EXPOSE 8000

# Default command: run the FastAPI app with uvicorn
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
