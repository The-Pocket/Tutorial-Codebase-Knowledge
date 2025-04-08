FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including Git and bash
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p logs output && chmod -R 777 logs output

# Expose the Streamlit port
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV LOG_DIR=/app/logs
ENV CACHE_FILE=/app/llm_cache.json
ENV CACHE_ENABLED=true
ENV GIT_PYTHON_REFRESH=quiet
ENV OUTPUT_DIR=/app/output

# Default command (can be overridden by docker-compose)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]