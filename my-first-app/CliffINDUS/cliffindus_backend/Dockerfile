# Use lightweight Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies (for psycopg2 and others)
RUN apt-get update && apt-get install -y netcat-traditional libpq-dev gcc && \
    apt-get clean

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project into the container
COPY . .

# Copy and prepare wait-for-db script
COPY wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

COPY requirements.txt .
RUN pip install -r requirements.txt

# Expose Django dev server port
EXPOSE 8000

# Command will be overridden by docker-compose
CMD ["/wait-for-db.sh", "python", "manage.py", "runserver", "0.0.0.0:8000"]
