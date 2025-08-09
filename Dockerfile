# Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's source code to the working directory
COPY . .

# Cloud Run sets the PORT environment variable
ENV PORT=8080

# Expose the port the app runs on
EXPOSE 8080

# Run gunicorn to serve the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
