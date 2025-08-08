"""
Unit tests for MemoryManager.

Tests memory monitoring, agent spawning decisions, and consolidation strategies.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.autonomous_agents.memory_manager import (
    MemoryManager,
    MemoryStats,
    MemoryThreshold,
    AgentMemoryProfile
)


class TestMemoryManager:
    """Test suite for MemoryManager."""
    
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
    
    def test_init_environment_variables(self):
        """Test MemoryManager initialization from environment variables."""
        with patch.dict('os.environ', {
            'MAX_MEMORY_GB': '12.0',
            'MEMORY_SAFETY_MARGIN': '0.20'
        }):
            memory_manager = MemoryManager()
            
            assert memory_manager.max_memory_gb == 12.0
            assert memory_manager.safety_margin == 0.20
    
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
    def test_get_current_stats_low_memory(self, mock_memory):
        """Test memory stats calculation for low memory scenario."""
        # Mock 8GB total, 1.5GB available (81.25% usage)
        mock_memory.return_value = MagicMock(
            total=8 * 1024**3,
            available=1.5 * 1024**3,
            percent=81.25
        )
        
        memory_manager = MemoryManager(max_memory_gb=8.0)
        stats = memory_manager.get_current_stats()
        
        assert stats.total_gb == 8.0
        assert stats.available_gb == 1.5
        assert stats.used_percent == 81.25
        assert stats.threshold_level == MemoryThreshold.LOW
        assert stats.can_spawn_agents is False  # 1.5GB < 30% of 6.8GB usable
        assert stats.recommended_agent_count == 2
    
    @patch('app.autonomous_agents.memory_manager.psutil.virtual_memory')
    def test_get_current_stats_exception_handling(self, mock_memory):
        """Test memory stats with psutil exception."""
        mock_memory.side_effect = Exception("psutil error")
        
        memory_manager = MemoryManager()
        stats = memory_manager.get_current_stats()
        
        # Should return safe defaults
        assert stats.total_gb == 8.0
        assert stats.available_gb == 2.0
        assert stats.used_percent == 75.0
        assert stats.threshold_level == MemoryThreshold.LOW
        assert stats.can_spawn_agents is False
        assert stats.recommended_agent_count == 1
    
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
    
    @patch('app.autonomous_agents.memory_manager.psutil.virtual_memory')
    def test_can_spawn_agent_insufficient_memory(self, mock_memory):
        """Test agent spawning with insufficient memory."""
        # Mock 0.5GB available
        mock_memory.return_value = MagicMock(
            total=8 * 1024**3,
            available=0.5 * 1024**3,
            percent=93.75
        )
        
        memory_manager = MemoryManager()
        can_spawn, reason = memory_manager.can_spawn_agent("pdf_intelligence")
        
        assert can_spawn is False
        assert "Insufficient memory" in reason
    
    @patch('app.autonomous_agents.memory_manager.psutil.virtual_memory')
    def test_can_spawn_agent_unknown_type(self, mock_memory):
        """Test agent spawning with unknown agent type."""
        # Mock 8GB available
        mock_memory.return_value = MagicMock(
            total=16 * 1024**3,
            available=8 * 1024**3,
            percent=50.0
        )
        
        memory_manager = MemoryManager()
        can_spawn, reason = memory_manager.can_spawn_agent("unknown_agent")
        
        assert can_spawn is True  # Should use default estimate
        assert "Memory available" in reason
    
    @patch('app.autonomous_agents.memory_manager.psutil.virtual_memory')
    def test_can_spawn_agent_with_custom_memory(self, mock_memory):
        """Test agent spawning with custom memory estimate."""
        # Mock 1GB available
        mock_memory.return_value = MagicMock(
            total=8 * 1024**3,
            available=1 * 1024**3,
            percent=87.5
        )
        
        memory_manager = MemoryManager()
        
        # Try to spawn agent requiring 2GB (2048MB)
        can_spawn, reason = memory_manager.can_spawn_agent("custom_agent", 2048)
        
        assert can_spawn is False
        assert "Insufficient memory" in reason
    
    @patch('app.autonomous_agents.memory_manager.psutil.virtual_memory')
    def test_can_spawn_agent_limit_reached(self, mock_memory):
        """Test agent spawning when agent limit is reached."""
        # Mock sufficient memory but set agents to limit
        mock_memory.return_value = MagicMock(
            total=8 * 1024**3,
            available=2 * 1024**3,  # 2GB available -> recommended count = 3
            percent=75.0
        )
        
        memory_manager = MemoryManager()
        
        # Simulate 3 active agents (at the limit)
        memory_manager.active_agents = {"agent1": 1, "agent2": 1, "agent3": 1}
        
        can_spawn, reason = memory_manager.can_spawn_agent("orchestrator")
        
        assert can_spawn is False
        assert "Insufficient memory" in reason
    
    def test_register_agent(self):
        """Test agent registration."""
        memory_manager = MemoryManager()
        
        memory_manager.register_agent("orchestrator")
        assert memory_manager.active_agents["orchestrator"] == 1
        
        memory_manager.register_agent("orchestrator")
        assert memory_manager.active_agents["orchestrator"] == 2
        
        memory_manager.register_agent("pdf_intelligence")
        assert memory_manager.active_agents["pdf_intelligence"] == 1
        assert len(memory_manager.active_agents) == 2
    
    def test_unregister_agent(self):
        """Test agent unregistration."""
        memory_manager = MemoryManager()
        
        # Register some agents
        memory_manager.active_agents = {"orchestrator": 2, "pdf_intelligence": 1}
        
        # Unregister one orchestrator
        memory_manager.unregister_agent("orchestrator")
        assert memory_manager.active_agents["orchestrator"] == 1
        
        # Unregister last orchestrator
        memory_manager.unregister_agent("orchestrator")
        assert "orchestrator" not in memory_manager.active_agents
        
        # Unregister pdf_intelligence
        memory_manager.unregister_agent("pdf_intelligence")
        assert memory_manager.active_agents == {}
        
        # Unregister non-existent agent (should not crash)
        memory_manager.unregister_agent("non_existent")
        assert memory_manager.active_agents == {}
    
    @patch('app.autonomous_agents.memory_manager.psutil.virtual_memory')
    def test_suggest_consolidation_strategy_high_memory(self, mock_memory):
        """Test consolidation strategy for high memory scenario."""
        # Mock 8GB available
        mock_memory.return_value = MagicMock(
            total=16 * 1024**3,
            available=8 * 1024**3,
            percent=50.0
        )
        
        memory_manager = MemoryManager()
        strategy = memory_manager.suggest_consolidation_strategy()
        
        assert strategy["threshold_level"] == 6.0  # HIGH threshold
        assert strategy["recommended_action"] == "spawn_specialized_agents"
        assert "orchestrator" in strategy["agent_consolidation"]
        assert "pdf_intelligence" in strategy["agent_consolidation"]
        assert "sub_agents" in strategy["agent_consolidation"]
    
    @patch('app.autonomous_agents.memory_manager.psutil.virtual_memory')
    def test_suggest_consolidation_strategy_medium_memory(self, mock_memory):
        """Test consolidation strategy for medium memory scenario."""
        # Mock 4GB available
        mock_memory.return_value = MagicMock(
            total=8 * 1024**3,
            available=4 * 1024**3,
            percent=50.0
        )
        
        memory_manager = MemoryManager()
        strategy = memory_manager.suggest_consolidation_strategy()
        
        assert strategy["threshold_level"] == 3.0  # MEDIUM threshold
        assert strategy["recommended_action"] == "moderate_consolidation"
        assert "document_processing" in strategy["agent_consolidation"]
        assert "unload_models_after_use" in strategy["memory_optimizations"]
    
    @patch('app.autonomous_agents.memory_manager.psutil.virtual_memory')
    def test_suggest_consolidation_strategy_low_memory(self, mock_memory):
        """Test consolidation strategy for low memory scenario."""
        # Mock 1.5GB available
        mock_memory.return_value = MagicMock(
            total=8 * 1024**3,
            available=1.5 * 1024**3,
            percent=81.25
        )
        
        memory_manager = MemoryManager()
        strategy = memory_manager.suggest_consolidation_strategy()
        
        assert strategy["threshold_level"] == 1.0  # LOW threshold
        assert strategy["recommended_action"] == "aggressive_consolidation"
        assert "combined_processor" in strategy["agent_consolidation"]
        assert "sequential_processing" in strategy["memory_optimizations"]
    
    @patch('app.autonomous_agents.memory_manager.psutil.virtual_memory')
    def test_suggest_consolidation_strategy_critical_memory(self, mock_memory):
        """Test consolidation strategy for critical memory scenario."""
        # Mock 0.3GB available
        mock_memory.return_value = MagicMock(
            total=8 * 1024**3,
            available=0.3 * 1024**3,
            percent=96.25
        )
        
        memory_manager = MemoryManager()
        strategy = memory_manager.suggest_consolidation_strategy()
        
        assert strategy["threshold_level"] == 0.5  # CRITICAL threshold
        assert strategy["recommended_action"] == "minimal_mode"
        assert "orchestrator_only" in strategy["agent_consolidation"]
        assert "aggressive_garbage_collection" in strategy["memory_optimizations"]
    
    def test_determine_threshold_levels(self):
        """Test threshold determination for different memory levels."""
        memory_manager = MemoryManager()
        
        assert memory_manager._determine_threshold(8.0) == MemoryThreshold.HIGH
        assert memory_manager._determine_threshold(6.0) == MemoryThreshold.HIGH
        assert memory_manager._determine_threshold(5.9) == MemoryThreshold.MEDIUM
        assert memory_manager._determine_threshold(3.0) == MemoryThreshold.MEDIUM
        assert memory_manager._determine_threshold(2.9) == MemoryThreshold.LOW
        assert memory_manager._determine_threshold(1.0) == MemoryThreshold.LOW
        assert memory_manager._determine_threshold(0.9) == MemoryThreshold.CRITICAL
        assert memory_manager._determine_threshold(0.1) == MemoryThreshold.CRITICAL
    
    def test_calculate_recommended_agent_count(self):
        """Test recommended agent count calculation."""
        memory_manager = MemoryManager()
        
        assert memory_manager._calculate_recommended_agent_count(8.0) == 8
        assert memory_manager._calculate_recommended_agent_count(6.0) == 8
        assert memory_manager._calculate_recommended_agent_count(5.0) == 5
        assert memory_manager._calculate_recommended_agent_count(4.0) == 5
        assert memory_manager._calculate_recommended_agent_count(3.0) == 3
        assert memory_manager._calculate_recommended_agent_count(2.0) == 3
        assert memory_manager._calculate_recommended_agent_count(1.5) == 2
        assert memory_manager._calculate_recommended_agent_count(1.0) == 2
        assert memory_manager._calculate_recommended_agent_count(0.5) == 1
        assert memory_manager._calculate_recommended_agent_count(0.1) == 1


@pytest.fixture
def memory_manager():
    """Fixture providing a MemoryManager instance."""
    return MemoryManager(max_memory_gb=8.0)
