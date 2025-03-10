from fastapi import FastAPI
from celery_worker import add, multiply, subtract

app = FastAPI()

@app.get("/add")
def add_numbers(x: int, y: int):
    result = add.apply_async(args=(x, y), queue="low", routing_key="low")
    return {"task_id": result.id, "status": "processing", "queue": "low"}

@app.get("/multiply")
def multiply_numbers(x: int, y: int):
    result = multiply.apply_async(args=(x, y), queue="med", routing_key="med")
    return {"task_id": result.id, "status": "processing", "queue": "med"}

@app.get("/subtract")
def subtract_numbers(x: int, y: int):
    result = subtract.apply_async(args=(x, y), queue="high", routing_key="high")
    return {"task_id": result.id, "status": "processing", "queue": "high"}
