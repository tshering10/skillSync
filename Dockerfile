# Base Image
FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies list
COPY requirements.txt /app/

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download spaCy English model inside container image
RUN python -m spacy download en_core_web_sm

# Copy project files
COPY . /app/

# Expose port
EXPOSE 8000

# Start development server by default
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

