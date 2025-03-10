## new code

import logging
from celery import Celery, Task
from kombu import Exchange, Queue
from amqp.channel import Channel
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Patch AMQP basic_qos to always disable the global flag
_original_basic_qos = Channel.basic_qos

def _patched_basic_qos(self, prefetch_size=0, prefetch_count=0, global_=False):
    return _original_basic_qos(self, prefetch_size, prefetch_count, False)

Channel.basic_qos = _patched_basic_qos

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    'tasks',
    broker='pyamqp://guest:guest@rabbitmq//',
)

# Celery configuration
celery_app.conf.update(
    broker_transport_options={'visibility_timeout': 3600},  # Ensures tasks don’t expire too soon
    task_track_started=True,  # Allows tracking of started tasks
    worker_prefetch_multiplier=1,  # Ensures only one task is fetched at a time
    task_acks_late=True,  # Ensures acknowledgment happens only after execution
    task_reject_on_worker_lost=True,  # Prevents tasks from being lost if the worker dies
    task_default_exchange="custom_exchange",
    task_default_exchange_type="direct",
    task_default_routing_key="low",
    task_default_queue="low",
    task_create_missing_queues = False
)

# Define custom direct exchange
default_exchange = Exchange("custom_exchange", type="direct")

# Configure three **quorum queues** with custom exchange & routing
celery_app.conf.task_queues = (
    Queue("low", exchange=default_exchange, routing_key="low", queue_arguments={"x-queue-type": "quorum"}),
    Queue("med", exchange=default_exchange, routing_key="med", queue_arguments={"x-queue-type": "quorum"}),
    Queue("high", exchange=default_exchange, routing_key="high", queue_arguments={"x-queue-type": "quorum"}),
)

# Route tasks to appropriate queues
celery_app.conf.task_routes = {
    "celery_worker.add": {"queue": "low", "routing_key": "low"},
    "celery_worker.multiply": {"queue": "med", "routing_key": "med"},
    "celery_worker.subtract": {"queue": "high", "routing_key": "high"},
}

# Base Task class with logging
class BaseTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        routing_key = self.request.delivery_info.get('routing_key', 'unknown')
        logger.info(f"Task {self.name} succeeded on queue: {routing_key} with result: {retval}")

# Define tasks
@celery_app.task(name="celery_worker.add", bind=True, base=BaseTask)
def add(self, x, y):
    time.sleep(5)
    logger.info(f"Processing add on queue: {self.request.delivery_info['routing_key']}")
    return x + y

@celery_app.task(name="celery_worker.multiply", bind=True, base=BaseTask)
def multiply(self, x, y):
    time.sleep(5)
    logger.info(f"Processing multiply on queue: {self.request.delivery_info['routing_key']}")
    return x * y

@celery_app.task(name="celery_worker.subtract", bind=True, base=BaseTask)
def subtract(self, x, y):
    time.sleep(5)
    logger.info(f"Processing subtract on queue: {self.request.delivery_info['routing_key']}")
    return x - y



### Old Code 

# from celery import Celery, Task
# from kombu import Exchange, Queue
# import time

# celery_app = Celery(
#     'tasks',
#     broker='pyamqp://guest:guest@rabbitmq//',
# )

# # Ensure all tasks are acknowledged **only after execution**
# celery_app.conf.worker_prefetch_multiplier = 1
# celery_app.conf.task_acks_late = True
# celery_app.conf.task_reject_on_worker_lost = True
# celery_app.conf.task_create_missing_queues = False
# celery_app.conf.task_default_queue = "low"
# celery_app.conf.task_default_exchange = "custom_exchange"
# celery_app.conf.task_default_exchange_type = "direct"
# celery_app.conf.task_default_routing_key = "low"
# celery_app.conf.task_routes = {
#     "celery_worker.add": {"queue": "low", "routing_key": "low"},
#     "celery_worker.multiply": {"queue": "med", "routing_key": "med"},
#     "celery_worker.subtract": {"queue": "high", "routing_key": "high"},
# }

# # Define custom direct exchange
# default_exchange = Exchange("custom_exchange", type="direct")

# # Explicitly declare classic durable queues (no quorum)
# celery_app.conf.task_queues = (
#     Queue("low", exchange=default_exchange, routing_key="low", durable=True),
#     Queue("med", exchange=default_exchange, routing_key="med", durable=True),
#     Queue("high", exchange=default_exchange, routing_key="high", durable=True),
# )

# # Ensure tasks are only sent to existing queues
# celery_app.conf.task_create_missing_queues = False


# # Base task class to log queue details
# class BaseTask(Task):
#     def on_success(self, retval, task_id, args, kwargs):
#         routing_key = self.request.delivery_info.get('routing_key', 'unknown')
#         print(f"Task {self.name} succeeded on queue: {routing_key} with result: {retval}")

# # Define tasks
# @celery_app.task(name="celery_worker.add", bind=True, base=BaseTask)
# def add(self, x, y):
#     print(f"Processing add on queue: {self.request.delivery_info['routing_key']}")
#     return x + y

# @celery_app.task(name="celery_worker.multiply", bind=True, base=BaseTask)
# def multiply(self, x, y):
#     print(f"Processing multiply on queue: {self.request.delivery_info['routing_key']}")
#     return x * y

# @celery_app.task(name="celery_worker.subtract", bind=True, base=BaseTask)
# def subtract(self, x, y):
#     print(f"Processing subtract on queue: {self.request.delivery_info['routing_key']}")
#     return x - y
