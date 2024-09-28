# Use the official FastAPI image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Set working directory
WORKDIR /app

# Install dependencies
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install docker
# Copy application files
COPY ./webAPI/app /app

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run FastAPI application
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]