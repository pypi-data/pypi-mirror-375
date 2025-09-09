import os

# Get Redis URL from environment or use default
broker_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
result_backend = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True

# Memory optimization settings
result_expires = 3600  # Results expire after 1 hour
worker_max_tasks_per_child = 100  # Restart worker after 100 tasks
task_acks_late = True  # Only ack tasks after they're completed

# Broker connection settings
broker_connection_retry = True
broker_connection_retry_on_startup = True