# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy server script and HTML file
COPY server.py index.html ./

# Expose port 8081
EXPOSE 8001

# Run the server
CMD ["python3", "server.py"]

