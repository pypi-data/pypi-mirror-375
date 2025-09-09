# Import all tasks to make them discoverable by Celery
from .test_execution import run_single_test_task
from .orchestration import run_test_suite_task, run_test_suite_async_task, finalize_test_suite_task

__all__ = [
    'run_single_test_task', 
    'run_test_suite_task', 
    'run_test_suite_async_task',
    'finalize_test_suite_task'
]
