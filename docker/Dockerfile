# Use a lightweight Python image
FROM python:3.11.9-slim

# Set working directory
WORKDIR /app

# Copy the requirements file from the backend directory
COPY backend/requirements.txt .

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY backend .

# Expose API port
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "api:app", "--host=0.0.0.0", "--port=8000"]

