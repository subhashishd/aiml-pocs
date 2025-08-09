"""
Memory Manager for Autonomous Agents.

Handles real-time memory monitoring, agent spawning decisions, 
and resource optimization for the autonomous validation system.
"""

import os
import logging
import threading
from typing import Dict, Optional, Tuple
import psutil
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class MemoryThreshold(Enum):
    """Memory availability thresholds for agent management."""
    HIGH = 6.0      # >6GB available - Full agent ecosystem
    MEDIUM = 3.0    # 3-6GB available - Core agents + selective sub-agents  
    LOW = 1.0       # 1-3GB available - Consolidated agents
    CRITICAL = 0.5  # <1GB available - Single orchestrator only


@dataclass
class MemoryStats:
    """Current memory statistics."""
    total_gb: float
    available_gb: float
    used_percent: float
    threshold_level: MemoryThreshold
    can_spawn_agents: bool
    recommended_agent_count: int


@dataclass
class AgentMemoryProfile:
    """Memory profile for different agent types."""
    base_memory_mb: int
    peak_memory_mb: int
    model_memory_mb: int
    scaling_factor: float = 1.0


class MemoryManager:
    """
    Centralized memory management for autonomous agents.
    
    Tracks memory usage, makes spawning decisions, and optimizes
    resource allocation across the agent ecosystem.
    """
    
    # Agent memory profiles (estimated requirements)
    AGENT_PROFILES = {
        "orchestrator": AgentMemoryProfile(128, 256, 0, 1.0),
        "pdf_intelligence": AgentMemoryProfile(256, 512, 1024, 1.2),  # BLIP model
        "excel_intelligence": AgentMemoryProfile(128, 256, 0, 1.0),
        "validation": AgentMemoryProfile(256, 512, 512, 1.1),  # Embedding model
        "evaluation": AgentMemoryProfile(64, 128, 0, 0.8),
        "ocr_sub_agent": AgentMemoryProfile(128, 256, 256, 1.0),
        "multimodal_sub_agent": AgentMemoryProfile(512, 1024, 1536, 1.5),  # BLIP + processing
    }
    
    def __init__(self, max_memory_gb: Optional[float] = None):
        """
        Initialize memory manager.
        
        Args:
            max_memory_gb: Maximum memory limit. If None, auto-detect from environment.
        """
        self.max_memory_gb = max_memory_gb or float(os.getenv("MAX_MEMORY_GB", "8"))
        self.safety_margin = float(os.getenv("MEMORY_SAFETY_MARGIN", "0.15"))
        self.active_agents: Dict[str, int] = {}  # agent_type -> count
        self.agent_lock = threading.RLock()  # Reentrant lock for nested calls
        
        logger.info(f"MemoryManager initialized: max={self.max_memory_gb}GB, safety={self.safety_margin}")
    
    def get_current_stats(self) -> MemoryStats:
        """Get current memory statistics and recommendations."""
        try:
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024**3)
            available_gb = memory.available / (1024**3)
            used_percent = memory.percent
            
            # Determine threshold level
            threshold_level = self._determine_threshold(available_gb)
            
            # Calculate if we can spawn agents
            usable_memory = self.max_memory_gb * (1 - self.safety_margin)
            can_spawn = available_gb > (usable_memory * 0.3)  # Need at least 30% of usable memory
            
            # Recommend agent count based on available memory
            recommended_count = self._calculate_recommended_agent_count(available_gb)
            
            return MemoryStats(
                total_gb=total_gb,
                available_gb=available_gb,
                used_percent=used_percent,
                threshold_level=threshold_level,
                can_spawn_agents=can_spawn,
                recommended_agent_count=recommended_count
            )
            
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            # Return safe defaults
            return MemoryStats(
                total_gb=8.0,
                available_gb=2.0,
                used_percent=75.0,
                threshold_level=MemoryThreshold.LOW,
                can_spawn_agents=False,
                recommended_agent_count=1
            )
    
    def can_spawn_agent(
        self, 
        agent_type: str, 
        estimated_memory_mb: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Check if we can spawn a new agent of the given type.
        Uses atomic operations to prevent race conditions.
        
        Args:
            agent_type: Type of agent to spawn
            estimated_memory_mb: Override memory estimate
            
        Returns:
            Tuple of (can_spawn, reason)
        """
        with self.agent_lock:  # Atomic operation
            try:
                stats = self.get_current_stats()
                
                if not stats.can_spawn_agents:
                    return False, f"Insufficient memory: {stats.available_gb:.1f}GB available"
                
                # Get memory requirements for this agent type
                if estimated_memory_mb:
                    required_mb = estimated_memory_mb
                else:
                    profile = self.AGENT_PROFILES.get(agent_type)
                    if not profile:
                        logger.warning(f"Unknown agent type: {agent_type}")
                        required_mb = 256  # Default estimate
                    else:
                        required_mb = profile.peak_memory_mb + profile.model_memory_mb
                
                required_gb = required_mb / 1024
                
                # Check if we have enough memory
                if stats.available_gb < required_gb:
                    return False, f"Insufficient memory: need {required_gb:.1f}GB, have {stats.available_gb:.1f}GB"
                
                # Check threshold-based limits atomically
                current_agent_count = sum(self.active_agents.values())
                if current_agent_count >= stats.recommended_agent_count:
                    return False, f"Agent limit reached: {current_agent_count}/{stats.recommended_agent_count}"
                
                return True, "Memory available for agent spawning"
                
            except Exception as e:
                logger.error(f"Error checking agent spawn capability: {e}")
                return False, f"Error checking memory: {e}"
    
    def try_spawn_agent(
        self, 
        agent_type: str, 
        estimated_memory_mb: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Atomically check and reserve an agent slot if available.
        This prevents race conditions in concurrent spawning.
        
        Args:
            agent_type: Type of agent to spawn
            estimated_memory_mb: Override memory estimate
            
        Returns:
            Tuple of (can_spawn, reason)
        """
        with self.agent_lock:  # Atomic check and reserve
            can_spawn, reason = self.can_spawn_agent(agent_type, estimated_memory_mb)
            
            if can_spawn:
                # Immediately reserve the slot
                self.active_agents[agent_type] = self.active_agents.get(agent_type, 0) + 1
                logger.info(f"Reserved slot for {agent_type} agent. Active agents: {self.active_agents}")
            
            return can_spawn, reason
    
    def register_agent(self, agent_type: str) -> None:
        """Register a new agent as active with atomic operation."""
        with self.agent_lock:
            self.active_agents[agent_type] = self.active_agents.get(agent_type, 0) + 1
            logger.info(f"Registered {agent_type} agent. Active agents: {self.active_agents}")
    
    def unregister_agent(self, agent_type: str) -> None:
        """Unregister an agent (when it completes or fails) with atomic operation."""
        with self.agent_lock:
            if agent_type in self.active_agents and self.active_agents[agent_type] > 0:
                self.active_agents[agent_type] -= 1
                if self.active_agents[agent_type] == 0:
                    del self.active_agents[agent_type]
                logger.info(f"Unregistered {agent_type} agent. Active agents: {self.active_agents}")
    
    def suggest_consolidation_strategy(self) -> Dict[str, any]:
        """
        Suggest agent consolidation strategy based on memory pressure.
        
        Returns:
            Dictionary with consolidation recommendations
        """
        stats = self.get_current_stats()
        
        strategy = {
            "threshold_level": stats.threshold_level.value,
            "recommended_action": "",
            "agent_consolidation": {},
            "memory_optimizations": []
        }
        
        if stats.threshold_level == MemoryThreshold.HIGH:
            strategy["recommended_action"] = "spawn_specialized_agents"
            strategy["agent_consolidation"] = {
                "orchestrator": 1,
                "pdf_intelligence": 1,
                "excel_intelligence": 1, 
                "validation": 1,
                "sub_agents": ["ocr", "multimodal", "evaluation"]
            }
            
        elif stats.threshold_level == MemoryThreshold.MEDIUM:
            strategy["recommended_action"] = "moderate_consolidation"
            strategy["agent_consolidation"] = {
                "orchestrator": 1,
                "document_processing": 1,  # PDF + Excel combined
                "validation": 1
            }
            strategy["memory_optimizations"] = ["unload_models_after_use"]
            
        elif stats.threshold_level == MemoryThreshold.LOW:
            strategy["recommended_action"] = "aggressive_consolidation"
            strategy["agent_consolidation"] = {
                "orchestrator": 1,
                "combined_processor": 1  # All processing in one agent
            }
            strategy["memory_optimizations"] = [
                "unload_models_after_use",
                "sequential_processing", 
                "reduce_batch_sizes"
            ]
            
        else:  # CRITICAL
            strategy["recommended_action"] = "minimal_mode"
            strategy["agent_consolidation"] = {
                "orchestrator_only": 1  # Everything in orchestrator
            }
            strategy["memory_optimizations"] = [
                "unload_models_after_use",
                "sequential_processing",
                "minimal_batch_sizes",
                "aggressive_garbage_collection"
            ]
        
        return strategy
    
    def _determine_threshold(self, available_gb: float) -> MemoryThreshold:
        """Determine memory threshold level based on available memory."""
        if available_gb >= MemoryThreshold.HIGH.value:
            return MemoryThreshold.HIGH
        elif available_gb >= MemoryThreshold.MEDIUM.value:
            return MemoryThreshold.MEDIUM
        elif available_gb >= MemoryThreshold.LOW.value:
            return MemoryThreshold.LOW
        else:
            return MemoryThreshold.CRITICAL
    
    def _calculate_recommended_agent_count(self, available_gb: float) -> int:
        """Calculate recommended number of agents based on available memory."""
        if available_gb >= 6.0:
            return 8  # Full ecosystem
        elif available_gb >= 4.0:
            return 5  # Core agents + some sub-agents
        elif available_gb >= 2.0:
            return 3  # Core agents only
        elif available_gb >= 1.0:
            return 2  # Consolidated agents
        else:
            return 1  # Single orchestrator
