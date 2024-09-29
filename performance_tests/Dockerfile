# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the necessary packages
RUN pip install --no-cache-dir asyncpg beanie motor

# Command to run the Python script
CMD ["python","-u", "pg_vs_mongo.py"]

