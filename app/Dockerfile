FROM python:3.9-slim

WORKDIR /app

# Copy the requirements.txt from the project root into the container
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app code and the celery worker file
COPY app/fastapi_app.py .
COPY worker/celery_worker.py .

CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
