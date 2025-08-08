"""
Celery Worker Application for Autonomous Agent System.

Configures Celery app and registers all autonomous agents.
"""

import os
from celery import Celery
from kombu import Queue

# Initialize Celery app
app = Celery('autonomous_agents')

# Configure Celery
app.conf.update(
    broker_url=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=True,
    task_reject_on_worker_lost=True,
    
    # Queue configuration for different agent types
    task_routes={
        'app.autonomous_agents.orchestrator.pdf_intelligence_task': {'queue': 'pdf_processing'},
        'app.autonomous_agents.orchestrator.excel_intelligence_task': {'queue': 'excel_processing'},
        'app.autonomous_agents.orchestrator.validation_task': {'queue': 'validation'},
        'app.autonomous_agents.orchestrator.ocr_task': {'queue': 'ocr_processing'},
        'app.autonomous_agents.intelligent_agents.*': {'queue': 'intelligent_agents'},
    },
    
    task_default_queue='default',
    task_queues=(
        Queue('default'),
        Queue('pdf_processing'),
        Queue('excel_processing'),
        Queue('validation'),
        Queue('ocr_processing'),
        Queue('intelligent_agents'),
    ),
    
    # Memory optimization settings
    worker_max_tasks_per_child=100,
    worker_max_memory_per_child=2000000,  # 2GB per worker child
    
    # Beat schedule for autonomous monitoring
    beat_schedule={
        'memory-health-check': {
            'task': 'app.autonomous_agents.orchestrator.memory_health_check',
            'schedule': 30.0,  # Every 30 seconds
        },
        'agent-consolidation-check': {
            'task': 'app.autonomous_agents.orchestrator.consolidation_check',
            'schedule': 60.0,  # Every minute
        },
    },
)

# Auto-discover tasks from the autonomous_agents module
app.autodiscover_tasks(['app.autonomous_agents.orchestrator', 'app.autonomous_agents.intelligent_agents'])

if __name__ == '__main__':
    app.start()
