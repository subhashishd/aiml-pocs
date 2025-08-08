"""
Memory Monitor Service for Autonomous Agent System.

Continuously monitors system memory, logs telemetry, and triggers
consolidation actions when memory pressure is detected.
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, Any
import psutil
import asyncio

from app.autonomous_agents.memory_manager import MemoryManager, MemoryThreshold
from app.autonomous_agents.orchestrator import orchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MemoryMonitorService:
    """
    Memory monitoring service that runs continuously and manages
    system memory health for autonomous agents.
    """
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.check_interval = float(os.environ.get('MEMORY_CHECK_INTERVAL', '30'))
        self.warning_threshold = float(os.environ.get('MEMORY_WARNING_THRESHOLD', '80'))
        self.critical_threshold = float(os.environ.get('MEMORY_CRITICAL_THRESHOLD', '90'))
        self.running = False
        self.telemetry_data = []
        
        logger.info(f"Memory monitor initialized - Check interval: {self.check_interval}s")
    
    def collect_telemetry(self) -> Dict[str, Any]:
        """
        Collect comprehensive memory and system telemetry.
        """
        try:
            # Get memory statistics
            stats = self.memory_manager.get_current_stats()
            
            # Get process-specific memory info
            process = psutil.Process()
            process_memory = process.memory_info()
            
            # Get system-wide memory info
            system_memory = psutil.virtual_memory()
            
            # Get active agent information
            active_tasks = len(orchestrator.active_tasks)
            task_types = list(orchestrator.active_tasks.values())
            
            telemetry = {
                "timestamp": datetime.now().isoformat(),
                "memory_stats": {
                    "total_gb": stats.total_gb,
                    "available_gb": stats.available_gb,
                    "used_percent": stats.used_percent,
                    "threshold_level": stats.threshold_level.name,
                    "can_spawn_agents": stats.can_spawn_agents,
                    "recommended_agent_count": stats.recommended_agent_count
                },
                "process_memory": {
                    "rss_mb": process_memory.rss / (1024 * 1024),
                    "vms_mb": process_memory.vms / (1024 * 1024),
                    "percent": process.memory_percent()
                },
                "system_memory": {
                    "total_gb": system_memory.total / (1024**3),
                    "available_gb": system_memory.available / (1024**3),
                    "percent": system_memory.percent,
                    "used_gb": system_memory.used / (1024**3),
                    "free_gb": system_memory.free / (1024**3)
                },
                "agent_status": {
                    "active_tasks": active_tasks,
                    "task_types": task_types,
                    "consolidation_active": orchestrator.consolidation_active
                },
                "cpu_stats": {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "cpu_count": psutil.cpu_count(),
                    "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
                }
            }
            
            return telemetry
            
        except Exception as e:
            logger.error(f"Error collecting telemetry: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }
    
    def check_memory_health(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze memory health and determine required actions.
        """
        try:
            memory_percent = telemetry["system_memory"]["percent"]
            threshold_level = telemetry["memory_stats"]["threshold_level"]
            
            health_status = {
                "status": "healthy",
                "alerts": [],
                "recommendations": [],
                "actions_required": []
            }
            
            # Check memory thresholds
            if memory_percent >= self.critical_threshold:
                health_status["status"] = "critical"
                health_status["alerts"].append(
                    f"CRITICAL: Memory usage at {memory_percent:.1f}% (threshold: {self.critical_threshold}%)"
                )
                health_status["actions_required"].extend([
                    "force_consolidation",
                    "kill_non_essential_processes",
                    "aggressive_garbage_collection"
                ])
                
            elif memory_percent >= self.warning_threshold:
                health_status["status"] = "warning"
                health_status["alerts"].append(
                    f"WARNING: Memory usage at {memory_percent:.1f}% (threshold: {self.warning_threshold}%)"
                )
                health_status["actions_required"].extend([
                    "suggest_consolidation",
                    "unload_unused_models"
                ])
            
            # Check threshold-based recommendations
            if threshold_level == "CRITICAL":
                health_status["recommendations"].extend([
                    "Use minimal processing mode only",
                    "Reject new processing requests",
                    "Clear all caches"
                ])
            elif threshold_level == "LOW":
                health_status["recommendations"].extend([
                    "Use consolidated processing",
                    "Reduce batch sizes",
                    "Sequential processing only"
                ])
            
            # Check for agent overload
            active_tasks = telemetry["agent_status"]["active_tasks"]
            recommended_count = telemetry["memory_stats"]["recommended_agent_count"]
            
            if active_tasks > recommended_count:
                health_status["alerts"].append(
                    f"Agent overload: {active_tasks} active tasks, recommended: {recommended_count}"
                )
                health_status["actions_required"].append("consolidate_agents")
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error checking memory health: {e}")
            return {
                "status": "error",
                "error": str(e),
                "alerts": [f"Health check failed: {e}"]
            }
    
    def execute_memory_actions(self, actions: list) -> Dict[str, Any]:
        """
        Execute memory management actions.
        """
        results = {}
        
        for action in actions:
            try:
                if action == "force_consolidation":
                    strategy = self.memory_manager.suggest_consolidation_strategy()
                    results[action] = {
                        "status": "completed",
                        "strategy": strategy
                    }
                    logger.warning(f"Forced consolidation strategy: {strategy['recommended_action']}")
                
                elif action == "aggressive_garbage_collection":
                    import gc
                    collected = gc.collect()
                    results[action] = {
                        "status": "completed",
                        "objects_collected": collected
                    }
                    logger.info(f"Aggressive garbage collection completed: {collected} objects collected")
                
                elif action == "suggest_consolidation":
                    strategy = self.memory_manager.suggest_consolidation_strategy()
                    results[action] = {
                        "status": "suggested",
                        "strategy": strategy
                    }
                    logger.info(f"Consolidation suggested: {strategy['recommended_action']}")
                
                else:
                    results[action] = {
                        "status": "not_implemented",
                        "message": f"Action '{action}' not implemented yet"
                    }
                    
            except Exception as e:
                logger.error(f"Error executing action '{action}': {e}")
                results[action] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    def log_telemetry(self, telemetry: Dict[str, Any], health_status: Dict[str, Any]) -> None:
        """
        Log telemetry data for monitoring and analysis.
        """
        try:
            # Add telemetry to in-memory store (limited size)
            self.telemetry_data.append({
                "telemetry": telemetry,
                "health_status": health_status
            })
            
            # Keep only last 100 entries
            if len(self.telemetry_data) > 100:
                self.telemetry_data = self.telemetry_data[-100:]
            
            # Log summary
            memory_gb = telemetry["memory_stats"]["available_gb"]
            threshold = telemetry["memory_stats"]["threshold_level"]
            active_tasks = telemetry["agent_status"]["active_tasks"]
            
            logger.info(
                f"Memory Monitor - Available: {memory_gb:.1f}GB, "
                f"Threshold: {threshold}, Active Tasks: {active_tasks}, "
                f"Health: {health_status['status']}"
            )
            
            # Log alerts if any
            for alert in health_status.get("alerts", []):
                logger.warning(f"Memory Alert: {alert}")
            
            # TODO: Send to external monitoring system (InfluxDB, Prometheus, etc.)
            # self._send_to_monitoring_system(telemetry, health_status)
            
        except Exception as e:
            logger.error(f"Error logging telemetry: {e}")
    
    async def monitor_loop(self) -> None:
        """
        Main monitoring loop.
        """
        logger.info("Starting memory monitoring loop")
        self.running = True
        
        while self.running:
            try:
                # Collect telemetry
                telemetry = self.collect_telemetry()
                
                # Check memory health
                health_status = self.check_memory_health(telemetry)
                
                # Execute actions if required
                actions_required = health_status.get("actions_required", [])
                if actions_required:
                    action_results = self.execute_memory_actions(actions_required)
                    health_status["action_results"] = action_results
                
                # Log telemetry
                self.log_telemetry(telemetry, health_status)
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in memory monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop(self) -> None:
        """
        Stop the monitoring loop.
        """
        logger.info("Stopping memory monitoring loop")
        self.running = False
    
    def get_recent_telemetry(self, limit: int = 10) -> list:
        """
        Get recent telemetry data.
        """
        return self.telemetry_data[-limit:] if self.telemetry_data else []


# Global monitor instance
monitor = MemoryMonitorService()


async def main():
    """
    Main function to run the memory monitor as a standalone service.
    """
    try:
        logger.info("Starting Memory Monitor Service")
        await monitor.monitor_loop()
    except KeyboardInterrupt:
        logger.info("Memory monitor stopped by user")
    except Exception as e:
        logger.error(f"Memory monitor failed: {e}")
    finally:
        monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())
