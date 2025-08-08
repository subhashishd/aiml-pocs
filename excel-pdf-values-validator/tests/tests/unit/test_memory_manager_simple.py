"""
Simple unit tests for MemoryManager to validate our approach.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.autonomous_agents.memory_manager import (
    MemoryManager,
    MemoryThreshold,
)


class TestMemoryManagerSimple:
    """Simple test suite for MemoryManager."""
    
    def test_init_default_values(self):
        """Test MemoryManager initialization with default values."""
        with patch.dict('os.environ', {}, clear=True):
            memory_manager = MemoryManager()
            
            assert memory_manager.max_memory_gb == 8.0
            assert memory_manager.safety_margin == 0.15
            assert memory_manager.active_agents == {}
    
    def test_init_custom_values(self):
        """Test MemoryManager initialization with custom values."""
        memory_manager = MemoryManager(max_memory_gb=16.0)
        assert memory_manager.max_memory_gb == 16.0
    
    @patch('app.autonomous_agents.memory_manager.psutil.virtual_memory')
    def test_get_current_stats_high_memory(self, mock_memory):
        """Test memory stats calculation for high memory scenario."""
        # Mock 16GB total, 8GB available (50% usage)
        mock_memory.return_value = MagicMock(
            total=16 * 1024**3,
            available=8 * 1024**3,
            percent=50.0
        )
        
        memory_manager = MemoryManager(max_memory_gb=8.0)
        stats = memory_manager.get_current_stats()
        
        assert stats.total_gb == 16.0
        assert stats.available_gb == 8.0
        assert stats.used_percent == 50.0
        assert stats.threshold_level == MemoryThreshold.HIGH
        assert stats.can_spawn_agents is True
        assert stats.recommended_agent_count == 8
    
    @patch('app.autonomous_agents.memory_manager.psutil.virtual_memory')
    def test_can_spawn_agent_sufficient_memory(self, mock_memory):
        """Test agent spawning with sufficient memory."""
        # Mock 8GB available
        mock_memory.return_value = MagicMock(
            total=16 * 1024**3,
            available=8 * 1024**3,
            percent=50.0
        )
        
        memory_manager = MemoryManager()
        can_spawn, reason = memory_manager.can_spawn_agent("pdf_intelligence")
        
        assert can_spawn is True
        assert "Memory available" in reason
    
    def test_register_unregister_agent(self):
        """Test agent registration and unregistration."""
        memory_manager = MemoryManager()
        
        # Test registration
        memory_manager.register_agent("orchestrator")
        assert memory_manager.active_agents["orchestrator"] == 1
        
        memory_manager.register_agent("orchestrator")
        assert memory_manager.active_agents["orchestrator"] == 2
        
        # Test unregistration
        memory_manager.unregister_agent("orchestrator")
        assert memory_manager.active_agents["orchestrator"] == 1
        
        memory_manager.unregister_agent("orchestrator")
        assert "orchestrator" not in memory_manager.active_agents
    
    def test_determine_threshold_levels(self):
        """Test threshold determination for different memory levels."""
        memory_manager = MemoryManager()
        
        assert memory_manager._determine_threshold(8.0) == MemoryThreshold.HIGH
        assert memory_manager._determine_threshold(4.0) == MemoryThreshold.MEDIUM
        assert memory_manager._determine_threshold(2.0) == MemoryThreshold.LOW
        assert memory_manager._determine_threshold(0.3) == MemoryThreshold.CRITICAL
