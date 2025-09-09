import os
from celery import Celery
from multiprocessing import cpu_count

# Import configuration settings
from .celeryconfig import broker_url, result_backend

# Create Celery app instance
celery_app = Celery('reggie')

# Apply configuration
celery_app.config_from_object('regression_testing_framework.celeryconfig')

# Configure for CPU-bound tasks with one task per processor
celery_app.conf.update(
    # Worker settings for CPU-bound tasks
    worker_prefetch_multiplier=1,  # One task per worker at a time
    task_acks_late=True,          # Acknowledge tasks after completion
    worker_disable_rate_limits=True,
    
    # Concurrency settings - will be overridden by command line
    worker_concurrency=cpu_count(),  # Default to all CPUs
    
    # Task routing and execution
    task_routes={
        'regression_testing_framework.tasks.*': {'queue': 'test_execution'},
    },
    
    # Result settings
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone
    timezone='UTC',
    enable_utc=True,
)

# Auto-discover tasks from the tasks module
celery_app.autodiscover_tasks(['regression_testing_framework.tasks'])

if __name__ == '__main__':
    celery_app.start()