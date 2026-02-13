FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
ENV PYTHONUNBUFFERED=1

# Install system dependencies (adjust if needed for specific packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment directory for database persistence
VOLUME /app/instance
VOLUME /app/migrations

EXPOSE 5001

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
