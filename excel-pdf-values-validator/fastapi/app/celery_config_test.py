"""
Celery configuration for testing environment.
"""

import os

# Test broker configuration
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6380/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6380/0')

# Task settings for testing
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True

# Faster task execution for tests
task_always_eager = os.getenv('CELERY_ALWAYS_EAGER', 'False').lower() == 'true'
task_eager_propagates = True

# Reduce timeouts for faster test execution
broker_connection_retry_on_startup = True
broker_connection_retry = True
broker_connection_max_retries = 3
result_expires = 300  # 5 minutes

# Worker settings for testing
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 50

# Routing for test tasks
task_routes = {
    'app.autonomous_agents.intelligent_agents.*': {'queue': 'test_queue'},
}

# Beat schedule (empty for tests)
beat_schedule = {}

# Logging
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'
