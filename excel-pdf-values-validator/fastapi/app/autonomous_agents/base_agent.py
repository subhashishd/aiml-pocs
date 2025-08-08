"""
Base Adaptive Agent Class for Celery Tasks.

Provides common functionality for all autonomous agents including
memory management, telemetry collection, and capability handling.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from celery import Task
from dataclasses import dataclass, asdict
from datetime import datetime

from .memory_manager import MemoryManager

logger = logging.getLogger(__name__)


@dataclass
class AgentTelemetry:
    """Telemetry data for agent performance tracking."""
    agent_id: str
    agent_type: str
    task_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    peak_memory_mb: Optional[float] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    capabilities_used: List[str] = None
    consolidation_mode: Optional[str] = None
    
    def __post_init__(self):
        if self.capabilities_used is None:
            self.capabilities_used = []


@dataclass
class AgentCapability:
    """Represents a capability that an agent can perform."""
    name: str
    memory_requirement_mb: int
    dependencies: List[str] = None
    can_consolidate: bool = True
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class MemoryConstraintError(Exception):
    """Raised when agent cannot be spawned due to memory constraints."""
    pass


class AdaptiveAgentTask(Task, ABC):
    """
    Base class for all autonomous agents.
    
    Provides memory management, telemetry collection, capability handling,
    and adaptive behavior based on resource constraints.
    """
    
    # Override in subclasses
    agent_type: str = "base_agent"
    base_capabilities: List[AgentCapability] = []
    
    def __init__(self):
        super().__init__()
        self.memory_manager = MemoryManager()
        self.absorbed_capabilities: List[AgentCapability] = []
        self.telemetry: Optional[AgentTelemetry] = None
        self._start_time: Optional[float] = None
        
    def before_start(self, task_id: str, args: tuple, kwargs: dict) -> None:
        """Called before task execution starts."""
        try:
            # Check memory constraints
            can_spawn, reason = self.memory_manager.can_spawn_agent(self.agent_type)
            if not can_spawn:
                logger.warning(f"Agent spawn denied: {reason}")
                # Don't raise exception - allow graceful degradation
                # raise MemoryConstraintError(f"Cannot spawn {self.agent_type}: {reason}")
            
            # Register agent
            self.memory_manager.register_agent(self.agent_type)
            
            # Initialize telemetry
            self.telemetry = AgentTelemetry(
                agent_id=f"{self.agent_type}_{task_id}",
                agent_type=self.agent_type,
                task_id=task_id,
                start_time=datetime.now(),
                capabilities_used=[]
            )
            
            self._start_time = time.time()
            
            logger.info(f"Starting {self.agent_type} agent (task_id: {task_id})")
            
        except Exception as e:
            logger.error(f"Error in before_start for {self.agent_type}: {e}")
            # Don't fail the task, just log the error
    
    def after_return(self, status: str, retval: Any, task_id: str, args: tuple, kwargs: dict, einfo: Any) -> None:
        """Called after task execution completes."""
        try:
            # Unregister agent
            self.memory_manager.unregister_agent(self.agent_type)
            
            # Complete telemetry
            if self.telemetry and self._start_time:
                self.telemetry.end_time = datetime.now()
                self.telemetry.duration_seconds = time.time() - self._start_time
                self.telemetry.success = status == "SUCCESS"
                
                # Log telemetry
                self._log_telemetry()
            
            logger.info(f"Completed {self.agent_type} agent (task_id: {task_id}, status: {status})")
            
        except Exception as e:
            logger.error(f"Error in after_return for {self.agent_type}: {e}")
    
    def on_failure(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo: Any) -> None:
        """Called when task fails."""
        try:
            # Unregister agent
            self.memory_manager.unregister_agent(self.agent_type)
            
            # Record failure in telemetry
            if self.telemetry:
                self.telemetry.success = False
                self.telemetry.error_message = str(exc)
                self.telemetry.end_time = datetime.now()
                if self._start_time:
                    self.telemetry.duration_seconds = time.time() - self._start_time
                
                # Log telemetry
                self._log_telemetry()
            
            logger.error(f"Failed {self.agent_type} agent (task_id: {task_id}): {exc}")
            
        except Exception as e:
            logger.error(f"Error in on_failure for {self.agent_type}: {e}")
    
    def absorb_capability(self, capability: AgentCapability) -> bool:
        """
        Absorb a capability from another agent due to memory constraints.
        
        Args:
            capability: The capability to absorb
            
        Returns:
            True if capability was successfully absorbed
        """
        try:
            if not capability.can_consolidate:
                logger.warning(f"Capability {capability.name} cannot be consolidated")
                return False
            
            # Check if we have memory for this capability
            stats = self.memory_manager.get_current_stats()
            required_gb = capability.memory_requirement_mb / 1024
            
            if stats.available_gb < required_gb:
                logger.warning(f"Insufficient memory to absorb capability {capability.name}")
                return False
            
            self.absorbed_capabilities.append(capability)
            
            if self.telemetry:
                self.telemetry.capabilities_used.append(capability.name)
                self.telemetry.consolidation_mode = "absorbed_capabilities"
            
            logger.info(f"Agent {self.agent_type} absorbed capability: {capability.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error absorbing capability {capability.name}: {e}")
            return False
    
    def can_handle_capability(self, capability_name: str) -> bool:
        """Check if this agent can handle a specific capability."""
        # Check base capabilities
        for cap in self.base_capabilities:
            if cap.name == capability_name:
                return True
        
        # Check absorbed capabilities
        for cap in self.absorbed_capabilities:
            if cap.name == capability_name:
                return True
        
        return False
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / (1024 * 1024)
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return 0.0
    
    def _log_telemetry(self) -> None:
        """Log agent telemetry data."""
        if not self.telemetry:
            return
        
        try:
            # Update memory usage
            self.telemetry.memory_usage_mb = self.get_memory_usage()
            
            # Convert to dict for logging
            telemetry_dict = asdict(self.telemetry)
            
            # Log structured telemetry
            logger.info(f"Agent telemetry: {telemetry_dict}")
            
            # TODO: Send to InfluxDB for time-series analysis
            # self._send_to_influxdb(telemetry_dict)
            
        except Exception as e:
            logger.error(f"Error logging telemetry: {e}")
    
    @abstractmethod
    def execute_main_logic(self, *args, **kwargs) -> Any:
        """
        Main agent logic - must be implemented by subclasses.
        
        This method should contain the core functionality of the agent.
        """
        pass
    
    def run(self, *args, **kwargs) -> Any:
        """
        Main task execution method.
        
        This wraps the main logic with common functionality like
        memory management and telemetry collection.
        """
        try:
            # Execute main agent logic
            result = self.execute_main_logic(*args, **kwargs)
            
            # Mark capabilities as used
            if self.telemetry:
                for cap in self.base_capabilities:
                    self.telemetry.capabilities_used.append(cap.name)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.agent_type} execution: {e}")
            raise
