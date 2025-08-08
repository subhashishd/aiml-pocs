"""
Celery application entry point.

Imports the configured Celery app from autonomous_agents.worker.
"""

from app.autonomous_agents.worker import app

# Expose the Celery app instance
__all__ = ['app']
