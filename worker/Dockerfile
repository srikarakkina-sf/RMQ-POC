FROM python:3.9-slim

WORKDIR /app

# Copy the requirements.txt from the project root into the container
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Copy the celery worker code from the worker directory
COPY worker/celery_worker.py .

CMD ["celery", "-A", "celery_worker.celery_app", "worker", "-Q", "low,med,high", "--loglevel=info"]

