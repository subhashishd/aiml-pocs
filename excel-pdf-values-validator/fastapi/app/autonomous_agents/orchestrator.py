"""
Adaptive Agent Orchestrator

Orchestrates the spawning and management of adaptive agents based on 
current system memory usage and task requirements. Supports dynamic 
capability assignment based on agent constraints.
"""

import tempfile
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from celery import shared_task
from celery.signals import worker_ready
from .base_agent import AdaptiveAgentTask, AgentCapability, MemoryConstraintError
from .memory_manager import MemoryManager, MemoryThreshold
from .intelligent_agents import (
    pdf_intelligence_task,
    excel_intelligence_task,
    validation_intelligence_task,
    consolidated_processing_task
)
import logging

logger = logging.getLogger(__name__)

class AdaptiveAgentOrchestrator:
    """
    Orchestrates adaptive agent execution based on resource availability.
    Manages task distribution, memory monitoring, and agent consolidation.
    """
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.active_tasks = {}
        self.consolidation_active = False
        
    def process_validation_request(
        self, 
        pdf_path: str, 
        excel_path: str, 
        pdf_filename: str, 
        excel_filename: str
    ) -> Dict[str, Any]:
        """
        Main entry point for processing validation requests.
        Determines optimal execution strategy based on memory availability.
        
        Args:
            pdf_path: Path to PDF file
            excel_path: Path to Excel file
            pdf_filename: PDF filename
            excel_filename: Excel filename
            
        Returns:
            Task execution results
        """
        try:
            stats = self.memory_manager.get_current_stats()
            strategy = self.memory_manager.suggest_consolidation_strategy()
            
            logger.info(f"Processing validation request - Memory: {stats.available_gb:.1f}GB, Threshold: {stats.threshold_level.name}")
            
            # Determine execution strategy
            if stats.threshold_level in [MemoryThreshold.HIGH, MemoryThreshold.MEDIUM]:
                return self._execute_distributed_processing(
                    pdf_path, excel_path, pdf_filename, excel_filename
                )
            else:
                return self._execute_consolidated_processing(
                    pdf_path, excel_path, pdf_filename, excel_filename
                )
                
        except Exception as e:
            logger.error(f"Error in orchestrator processing: {e}")
            raise
    
    def _execute_distributed_processing(
        self, 
        pdf_path: str, 
        excel_path: str, 
        pdf_filename: str, 
        excel_filename: str
    ) -> Dict[str, Any]:
        """
        Execute processing using separate specialized agents.
        """
        try:
            logger.info("Executing distributed processing strategy")
            
            # Submit PDF processing task
            pdf_task = pdf_intelligence_task.delay(pdf_path, pdf_filename)
            self.active_tasks[pdf_task.id] = "pdf_intelligence"
            
            # Submit Excel processing task
            excel_task = excel_intelligence_task.delay(excel_path, excel_filename)
            self.active_tasks[excel_task.id] = "excel_intelligence"
            
            # Wait for both tasks to complete
            pdf_result = pdf_task.get(timeout=300)  # 5 minute timeout
            excel_result = excel_task.get(timeout=300)
            
            # Clean up task tracking
            self.active_tasks.pop(pdf_task.id, None)
            self.active_tasks.pop(excel_task.id, None)
            
            # Submit validation task with results
            validation_task = validation_intelligence_task.delay(
                pdf_result['chunks'],
                excel_result['data'],
                pdf_filename,
                excel_filename
            )
            self.active_tasks[validation_task.id] = "validation_intelligence"
            
            # Get validation results
            validation_result = validation_task.get(timeout=300)
            self.active_tasks.pop(validation_task.id, None)
            
            return {
                "status": "success",
                "execution_mode": "distributed",
                "pdf_result": pdf_result,
                "excel_result": excel_result,
                "validation_result": validation_result,
                "memory_stats": self.memory_manager.get_current_stats().__dict__
            }
            
        except Exception as e:
            logger.error(f"Error in distributed processing: {e}")
            # Clean up any remaining tasks
            for task_id in list(self.active_tasks.keys()):
                self.active_tasks.pop(task_id, None)
            raise
    
    def _execute_consolidated_processing(
        self, 
        pdf_path: str, 
        excel_path: str, 
        pdf_filename: str, 
        excel_filename: str
    ) -> Dict[str, Any]:
        """
        Execute processing using a single consolidated agent.
        """
        try:
            logger.info("Executing consolidated processing strategy")
            self.consolidation_active = True
            
            # Submit consolidated processing task
            consolidated_task = consolidated_processing_task.delay(
                pdf_path, excel_path, pdf_filename, excel_filename
            )
            self.active_tasks[consolidated_task.id] = "consolidated_processing"
            
            # Wait for task completion
            result = consolidated_task.get(timeout=600)  # 10 minute timeout for consolidated processing
            
            # Clean up task tracking
            self.active_tasks.pop(consolidated_task.id, None)
            self.consolidation_active = False
            
            return {
                "status": "success",
                "execution_mode": "consolidated",
                "result": result,
                "memory_stats": self.memory_manager.get_current_stats().__dict__
            }
            
        except Exception as e:
            logger.error(f"Error in consolidated processing: {e}")
            self.consolidation_active = False
            # Clean up any remaining tasks
            for task_id in list(self.active_tasks.keys()):
                self.active_tasks.pop(task_id, None)
            raise
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status including memory and active tasks.
        """
        stats = self.memory_manager.get_current_stats()
        strategy = self.memory_manager.suggest_consolidation_strategy()
        
        return {
            "memory_stats": {
                "total_gb": stats.total_gb,
                "available_gb": stats.available_gb,
                "used_percent": stats.used_percent,
                "threshold_level": stats.threshold_level.name,
                "can_spawn_agents": stats.can_spawn_agents,
                "recommended_agent_count": stats.recommended_agent_count
            },
            "consolidation_strategy": strategy,
            "active_tasks": len(self.active_tasks),
            "task_types": list(self.active_tasks.values()),
            "consolidation_active": self.consolidation_active
        }


# Global orchestrator instance
orchestrator = AdaptiveAgentOrchestrator()


# Monitoring tasks
@shared_task(name="autonomous_agents.orchestrator.memory_health_check")
def memory_health_check():
    """
    Periodic memory health check task.
    """
    try:
        stats = orchestrator.memory_manager.get_current_stats()
        logger.info(f"Memory health check - Available: {stats.available_gb:.1f}GB, Threshold: {stats.threshold_level.name}")
        
        # Log warning if memory is low
        if stats.threshold_level == MemoryThreshold.CRITICAL:
            logger.warning("CRITICAL: Memory usage is critical, only minimal processing available")
        elif stats.threshold_level == MemoryThreshold.LOW:
            logger.warning("WARNING: Memory usage is high, consolidated processing recommended")
        
        return {
            "status": "completed",
            "memory_stats": stats.__dict__,
            "active_tasks": len(orchestrator.active_tasks)
        }
        
    except Exception as e:
        logger.error(f"Error in memory health check: {e}")
        return {"status": "error", "error": str(e)}


@shared_task(name="autonomous_agents.orchestrator.consolidation_check")
def consolidation_check():
    """
    Periodic check for agent consolidation opportunities.
    """
    try:
        stats = orchestrator.memory_manager.get_current_stats()
        strategy = orchestrator.memory_manager.suggest_consolidation_strategy()
        
        logger.info(f"Consolidation check - Recommended action: {strategy['recommended_action']}")
        
        # Log consolidation recommendations
        if strategy["recommended_action"] != "spawn_specialized_agents":
            logger.info(f"Consolidation recommended: {strategy['agent_consolidation']}")
            if strategy["memory_optimizations"]:
                logger.info(f"Memory optimizations: {strategy['memory_optimizations']}")
        
        return {
            "status": "completed",
            "consolidation_strategy": strategy,
            "active_tasks": len(orchestrator.active_tasks)
        }
        
    except Exception as e:
        logger.error(f"Error in consolidation check: {e}")
        return {"status": "error", "error": str(e)}


@shared_task(name="autonomous_agents.orchestrator.system_status")
def get_system_status():
    """
    Get current system status - can be called externally.
    """
    return orchestrator.get_system_status()

