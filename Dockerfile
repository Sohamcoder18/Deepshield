FROM python:3.11.8-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libchromaprint-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY poetry.lock pyproject.toml ./
COPY . .

# Install Poetry and dependencies
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Expose port
EXPOSE 5000

# Run gunicorn
CMD ["gunicorn", "wsgi:app", "--workers", "4", "--timeout", "120", "--bind", "0.0.0.0:5000"]
