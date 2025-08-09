"""
Prometheus Metrics Integration for Autonomous Agent System.

Provides comprehensive metrics collection, export, and monitoring
for agent performance, memory usage, and system health.
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, generate_latest
from prometheus_client.core import REGISTRY
import psutil
import os

logger = logging.getLogger(__name__)

class AgentMetrics:
    """
    Comprehensive metrics collection for autonomous agents.
    Integrates with Prometheus for monitoring and alerting.
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or REGISTRY
        
        # Agent execution metrics
        self.agent_tasks_total = Counter(
            'agent_tasks_total',
            'Total number of agent tasks executed',
            ['agent_type', 'status'],
            registry=self.registry
        )
        
        self.agent_task_duration = Histogram(
            'agent_task_duration_seconds',
            'Duration of agent task execution',
            ['agent_type'],
            buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0],
            registry=self.registry
        )
        
        self.agent_memory_usage = Histogram(
            'agent_memory_usage_mb',
            'Memory usage by agent type',
            ['agent_type'],
            buckets=[50, 100, 256, 512, 1024, 2048, 4096],
            registry=self.registry
        )
        
        # System metrics
        self.system_memory_total = Gauge(
            'system_memory_total_gb',
            'Total system memory in GB',
            registry=self.registry
        )
        
        self.system_memory_available = Gauge(
            'system_memory_available_gb',
            'Available system memory in GB',
            registry=self.registry
        )
        
        self.system_memory_used_percent = Gauge(
            'system_memory_used_percent',
            'System memory usage percentage',
            registry=self.registry
        )
        
        self.system_cpu_percent = Gauge(
            'system_cpu_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        # Agent orchestration metrics
        self.active_agents = Gauge(
            'active_agents_count',
            'Number of currently active agents',
            ['agent_type'],
            registry=self.registry
        )
        
        self.memory_threshold_level = Gauge(
            'memory_threshold_level',
            'Current memory threshold level (0=CRITICAL, 1=LOW, 2=MEDIUM, 3=HIGH)',
            registry=self.registry
        )
        
        self.consolidation_events = Counter(
            'consolidation_events_total',
            'Total number of consolidation events',
            ['trigger_reason'],
            registry=self.registry
        )
        
        self.processing_mode = Gauge(
            'processing_mode',
            'Current processing mode (0=minimal, 1=consolidated, 2=distributed)',
            registry=self.registry
        )
        
        # Task queue metrics
        self.queue_size = Gauge(
            'celery_queue_size',
            'Size of Celery task queues',
            ['queue_name'],
            registry=self.registry
        )
        
        self.task_failures = Counter(
            'task_failures_total',
            'Total number of task failures',
            ['task_type', 'error_type'],
            registry=self.registry
        )
        
        # Performance metrics
        self.pdf_processing_chunks = Histogram(
            'pdf_processing_chunks_count',
            'Number of chunks processed from PDF files',
            buckets=[1, 5, 10, 25, 50, 100, 200],
            registry=self.registry
        )
        
        self.excel_processing_rows = Histogram(
            'excel_processing_rows_count',
            'Number of rows processed from Excel files',
            buckets=[1, 10, 50, 100, 500, 1000, 5000],
            registry=self.registry
        )
        
        self.validation_accuracy = Histogram(
            'validation_accuracy_percent',
            'Validation accuracy percentage',
            buckets=[0, 50, 70, 80, 90, 95, 99, 100],
            registry=self.registry
        )
        
        # System info
        self.system_info = Info(
            'agent_system_info',
            'System information for the autonomous agent system',
            registry=self.registry
        )
        
        # Initialize system info
        self._update_system_info()
        
    def _update_system_info(self):
        """Update static system information."""
        try:
            self.system_info.info({
                'version': '2.0.0',
                'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                'platform': os.name,
                'cpu_count': str(psutil.cpu_count()),
                'startup_time': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error updating system info: {e}")
    
    def record_agent_task(self, agent_type: str, status: str, duration: float, memory_mb: float):
        """Record agent task execution metrics."""
        try:
            self.agent_tasks_total.labels(agent_type=agent_type, status=status).inc()
            self.agent_task_duration.labels(agent_type=agent_type).observe(duration)
            self.agent_memory_usage.labels(agent_type=agent_type).observe(memory_mb)
        except Exception as e:
            logger.error(f"Error recording agent task metrics: {e}")
    
    def update_system_metrics(self):
        """Update system-level metrics."""
        try:
            # Memory metrics
            memory = psutil.virtual_memory()
            self.system_memory_total.set(memory.total / (1024**3))
            self.system_memory_available.set(memory.available / (1024**3))
            self.system_memory_used_percent.set(memory.percent)
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.system_cpu_percent.set(cpu_percent)
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    def update_agent_metrics(self, active_agents: Dict[str, int]):
        """Update agent-specific metrics."""
        try:
            # Clear previous values
            for agent_type in ['pdf_intelligence', 'excel_intelligence', 'validation_intelligence', 'consolidated_processing']:
                self.active_agents.labels(agent_type=agent_type).set(0)
            
            # Set current values
            for agent_type, count in active_agents.items():
                self.active_agents.labels(agent_type=agent_type).set(count)
                
        except Exception as e:
            logger.error(f"Error updating agent metrics: {e}")
    
    def record_memory_threshold(self, threshold_level: str):
        """Record current memory threshold level."""
        try:
            threshold_map = {
                'CRITICAL': 0,
                'LOW': 1,
                'MEDIUM': 2,
                'HIGH': 3
            }
            level = threshold_map.get(threshold_level, 0)
            self.memory_threshold_level.set(level)
        except Exception as e:
            logger.error(f"Error recording memory threshold: {e}")
    
    def record_consolidation_event(self, trigger_reason: str):
        """Record a consolidation event."""
        try:
            self.consolidation_events.labels(trigger_reason=trigger_reason).inc()
        except Exception as e:
            logger.error(f"Error recording consolidation event: {e}")
    
    def record_processing_mode(self, mode: str):
        """Record current processing mode."""
        try:
            mode_map = {
                'minimal': 0,
                'consolidated': 1,
                'distributed': 2
            }
            mode_value = mode_map.get(mode, 0)
            self.processing_mode.set(mode_value)
        except Exception as e:
            logger.error(f"Error recording processing mode: {e}")
    
    def record_pdf_processing(self, chunk_count: int):
        """Record PDF processing metrics."""
        try:
            self.pdf_processing_chunks.observe(chunk_count)
        except Exception as e:
            logger.error(f"Error recording PDF processing metrics: {e}")
    
    def record_excel_processing(self, row_count: int):
        """Record Excel processing metrics."""
        try:
            self.excel_processing_rows.observe(row_count)
        except Exception as e:
            logger.error(f"Error recording Excel processing metrics: {e}")
    
    def record_validation_result(self, accuracy: float):
        """Record validation accuracy."""
        try:
            self.validation_accuracy.observe(accuracy)
        except Exception as e:
            logger.error(f"Error recording validation metrics: {e}")
    
    def record_task_failure(self, task_type: str, error_type: str):
        """Record task failure."""
        try:
            self.task_failures.labels(task_type=task_type, error_type=error_type).inc()
        except Exception as e:
            logger.error(f"Error recording task failure: {e}")
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        try:
            return generate_latest(self.registry).decode('utf-8')
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            return ""


# Global metrics instance - create lazily to avoid registry conflicts
_metrics_instance = None

def get_metrics_instance():
    """Get global metrics instance with lazy initialization."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = AgentMetrics()
    return _metrics_instance

# For backward compatibility
metrics = None  # Will be initialized when needed


class MetricsCollector:
    """
    Periodic metrics collection service.
    Runs in background to collect and update metrics.
    """
    
    def __init__(self, metrics_instance: AgentMetrics):
        self.metrics = metrics_instance
        self.collection_interval = float(os.environ.get('METRICS_COLLECTION_INTERVAL', '10'))
        self.running = False
    
    async def collect_loop(self):
        """Main metrics collection loop."""
        import asyncio
        
        logger.info("Starting metrics collection loop")
        self.running = True
        
        while self.running:
            try:
                # Update system metrics
                self.metrics.update_system_metrics()
                
                # Update agent metrics from orchestrator
                try:
                    from .orchestrator import orchestrator
                    self.metrics.update_agent_metrics(orchestrator.active_tasks)
                    
                    # Get system status for additional metrics
                    status = orchestrator.get_system_status()
                    if 'memory_stats' in status:
                        memory_stats = status['memory_stats']
                        self.metrics.record_memory_threshold(memory_stats['threshold_level'])
                    
                    if 'consolidation_active' in status and status['consolidation_active']:
                        self.metrics.record_processing_mode('consolidated')
                    else:
                        self.metrics.record_processing_mode('distributed')
                        
                except Exception as e:
                    logger.warning(f"Error collecting orchestrator metrics: {e}")
                
                # Wait for next collection
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(self.collection_interval)
    
    def stop(self):
        """Stop metrics collection."""
        logger.info("Stopping metrics collection")
        self.running = False


# Global collector instance
collector = MetricsCollector(metrics)
