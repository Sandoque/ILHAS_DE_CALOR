FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app:create_app \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    DATA_DIR=/app/data/inmet \
    START_YEAR=2010

# System deps for psycopg2/SQLAlchemy if needed
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ /app/
COPY etl/ /app/etl/
# Utility scripts for running ETL inside the container
COPY scripts/ /app/scripts/

# Prepare writable data directory and set ownership
RUN mkdir -p /app/data/inmet/raw /app/data/inmet/processed \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["gunicorn", "run_wsgi:app", "-b", "0.0.0.0:8000", "--workers", "3"]
