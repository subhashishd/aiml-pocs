"""
Comprehensive tests for the autonomous agent system.

Tests memory management, agent orchestration, intelligent agents,
and system integration.
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Test imports
import sys
sys.path.append('../app')

from app.autonomous_agents.memory_manager import MemoryManager, MemoryThreshold, MemoryStats
from app.autonomous_agents.base_agent import AdaptiveAgentTask, AgentCapability, MemoryConstraintError
from app.autonomous_agents.orchestrator import AdaptiveAgentOrchestrator
from app.autonomous_agents.intelligent_agents import (
    PDFIntelligenceAgent, 
    ExcelIntelligenceAgent, 
    ValidationIntelligenceAgent,
    ConsolidatedProcessingAgent
)
from app.autonomous_agents.memory_monitor import MemoryMonitorService

class TestMemoryManager:
    """Test suite for MemoryManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.memory_manager = MemoryManager(max_memory_gb=8.0)
    
    def test_memory_manager_initialization(self):
        """Test memory manager initialization."""
        assert self.memory_manager.max_memory_gb == 8.0
        assert self.memory_manager.safety_margin == 0.15
        assert self.memory_manager.active_agents == {}
    
    @patch('psutil.virtual_memory')
    def test_get_current_stats_high_memory(self, mock_memory):
        """Test memory stats calculation with high available memory."""
        # Mock high memory scenario
        mock_memory.return_value = Mock(
            total=16 * 1024**3,  # 16GB
            available=8 * 1024**3,  # 8GB available
            percent=50.0
        )
        
        stats = self.memory_manager.get_current_stats()
        
        assert isinstance(stats, MemoryStats)
        assert stats.total_gb == 16.0
        assert stats.available_gb == 8.0
        assert stats.used_percent == 50.0
        assert stats.threshold_level == MemoryThreshold.HIGH
        assert stats.can_spawn_agents is True
        assert stats.recommended_agent_count == 8
    
    @patch('psutil.virtual_memory')
    def test_get_current_stats_low_memory(self, mock_memory):
        """Test memory stats calculation with low available memory."""
        # Mock low memory scenario
        mock_memory.return_value = Mock(
            total=8 * 1024**3,  # 8GB
            available=1.5 * 1024**3,  # 1.5GB available
            percent=81.25
        )
        
        stats = self.memory_manager.get_current_stats()
        
        assert stats.available_gb == 1.5
        assert stats.threshold_level == MemoryThreshold.LOW
        assert stats.recommended_agent_count == 2
    
    def test_can_spawn_agent_sufficient_memory(self):
        """Test agent spawning with sufficient memory."""
        with patch.object(self.memory_manager, 'get_current_stats') as mock_stats:
            mock_stats.return_value = MemoryStats(
                total_gb=16.0,
                available_gb=8.0,
                used_percent=50.0,
                threshold_level=MemoryThreshold.HIGH,
                can_spawn_agents=True,
                recommended_agent_count=8
            )
            
            can_spawn, reason = self.memory_manager.can_spawn_agent('pdf_intelligence')
            
            assert can_spawn is True
            assert "Memory available" in reason
    
    def test_can_spawn_agent_insufficient_memory(self):
        """Test agent spawning with insufficient memory."""
        with patch.object(self.memory_manager, 'get_current_stats') as mock_stats:
            mock_stats.return_value = MemoryStats(
                total_gb=8.0,
                available_gb=0.5,
                used_percent=93.75,
                threshold_level=MemoryThreshold.CRITICAL,
                can_spawn_agents=False,
                recommended_agent_count=1
            )
            
            can_spawn, reason = self.memory_manager.can_spawn_agent('pdf_intelligence')
            
            assert can_spawn is False
            assert "Insufficient memory" in reason
    
    def test_register_and_unregister_agent(self):
        """Test agent registration and unregistration."""
        # Register agents
        self.memory_manager.register_agent('pdf_intelligence')
        self.memory_manager.register_agent('pdf_intelligence')
        self.memory_manager.register_agent('excel_intelligence')
        
        assert self.memory_manager.active_agents['pdf_intelligence'] == 2
        assert self.memory_manager.active_agents['excel_intelligence'] == 1
        
        # Unregister agents
        self.memory_manager.unregister_agent('pdf_intelligence')
        assert self.memory_manager.active_agents['pdf_intelligence'] == 1
        
        self.memory_manager.unregister_agent('pdf_intelligence')
        assert 'pdf_intelligence' not in self.memory_manager.active_agents
        
        self.memory_manager.unregister_agent('excel_intelligence')
        assert 'excel_intelligence' not in self.memory_manager.active_agents
    
    def test_suggest_consolidation_strategy(self):
        """Test consolidation strategy suggestions."""
        with patch.object(self.memory_manager, 'get_current_stats') as mock_stats:
            # Test high memory scenario
            mock_stats.return_value = MemoryStats(
                total_gb=16.0,
                available_gb=8.0,
                used_percent=50.0,
                threshold_level=MemoryThreshold.HIGH,
                can_spawn_agents=True,
                recommended_agent_count=8
            )
            
            strategy = self.memory_manager.suggest_consolidation_strategy()
            
            assert strategy['recommended_action'] == 'spawn_specialized_agents'
            assert 'orchestrator' in strategy['agent_consolidation']
            assert 'pdf_intelligence' in strategy['agent_consolidation']
            
            # Test critical memory scenario
            mock_stats.return_value = MemoryStats(
                total_gb=8.0,
                available_gb=0.3,
                used_percent=96.25,
                threshold_level=MemoryThreshold.CRITICAL,
                can_spawn_agents=False,
                recommended_agent_count=1
            )
            
            strategy = self.memory_manager.suggest_consolidation_strategy()
            
            assert strategy['recommended_action'] == 'minimal_mode'
            assert 'orchestrator_only' in strategy['agent_consolidation']
            assert 'aggressive_garbage_collection' in strategy['memory_optimizations']


class TestAdaptiveAgentTask:
    """Test suite for AdaptiveAgentTask base class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        
        class TestAgent(AdaptiveAgentTask):
            agent_type = "test_agent"
            base_capabilities = [
                AgentCapability("test_capability", 256)
            ]
            
            def execute_main_logic(self, *args, **kwargs):
                return {"status": "success", "data": "test_result"}
        
        self.test_agent = TestAgent()
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        assert self.test_agent.agent_type == "test_agent"
        assert len(self.test_agent.base_capabilities) == 1
        assert self.test_agent.base_capabilities[0].name == "test_capability"
        assert self.test_agent.absorbed_capabilities == []
        assert self.test_agent.telemetry is None
    
    def test_capability_absorption(self):
        """Test capability absorption functionality."""
        new_capability = AgentCapability("additional_capability", 128)
        
        with patch.object(self.test_agent.memory_manager, 'get_current_stats') as mock_stats:
            mock_stats.return_value = MemoryStats(
                total_gb=16.0,
                available_gb=8.0,
                used_percent=50.0,
                threshold_level=MemoryThreshold.HIGH,
                can_spawn_agents=True,
                recommended_agent_count=8
            )
            
            success = self.test_agent.absorb_capability(new_capability)
            
            assert success is True
            assert new_capability in self.test_agent.absorbed_capabilities
    
    def test_can_handle_capability(self):
        """Test capability handling checks."""
        # Test base capability
        assert self.test_agent.can_handle_capability("test_capability") is True
        
        # Test non-existent capability
        assert self.test_agent.can_handle_capability("non_existent") is False
        
        # Test absorbed capability
        absorbed_cap = AgentCapability("absorbed_capability", 128)
        self.test_agent.absorbed_capabilities.append(absorbed_cap)
        assert self.test_agent.can_handle_capability("absorbed_capability") is True
    
    @patch('psutil.Process')
    def test_get_memory_usage(self, mock_process):
        """Test memory usage calculation."""
        mock_process.return_value.memory_info.return_value = Mock(rss=256 * 1024 * 1024)  # 256MB
        
        memory_usage = self.test_agent.get_memory_usage()
        assert memory_usage == 256.0


class TestAdaptiveAgentOrchestrator:
    """Test suite for AdaptiveAgentOrchestrator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = AdaptiveAgentOrchestrator()
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        assert isinstance(self.orchestrator.memory_manager, MemoryManager)
        assert self.orchestrator.active_tasks == {}
        assert self.orchestrator.consolidation_active is False
    
    def test_process_validation_request_distributed(self, temp_files):
        """Test distributed processing strategy."""
        pdf_path, excel_path = temp_files
        
        # Mock the orchestrator's intelligent_agents module import
        with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:
            mock_stats.return_value = MemoryStats(
                total_gb=16.0,
                available_gb=8.0,
                used_percent=50.0,
                threshold_level=MemoryThreshold.HIGH,
                can_spawn_agents=True,
                recommended_agent_count=8
            )
            
            # Mock the tasks directly in the orchestrator module
            with patch('app.autonomous_agents.orchestrator.pdf_intelligence_task') as mock_pdf_task, \
                 patch('app.autonomous_agents.orchestrator.excel_intelligence_task') as mock_excel_task, \
                 patch('app.autonomous_agents.orchestrator.validation_intelligence_task') as mock_validation_task:
                
                # Mock task results with proper result objects
                pdf_result_mock = MagicMock()
                pdf_result_mock.get.return_value = {
                    'status': 'success',
                    'chunks': [{'text': 'test chunk'}],
                    'chunk_count': 1
                }
                pdf_result_mock.id = 'pdf_task_123'
                mock_pdf_task.delay.return_value = pdf_result_mock
                
                excel_result_mock = MagicMock()
                excel_result_mock.get.return_value = {
                    'status': 'success',
                    'data': [{'parameter': 'test', 'value': 'value'}],
                    'row_count': 1
                }
                excel_result_mock.id = 'excel_task_456'
                mock_excel_task.delay.return_value = excel_result_mock
                
                validation_result_mock = MagicMock()
                validation_result_mock.get.return_value = {
                    'status': 'success',
                    'validation_result': {'matches': 1, 'mismatches': 0}
                }
                validation_result_mock.id = 'validation_task_789'
                mock_validation_task.delay.return_value = validation_result_mock
                
                result = self.orchestrator.process_validation_request(
                    pdf_path=pdf_path,
                    excel_path=excel_path,
                    pdf_filename='test.pdf',
                    excel_filename='test.xlsx'
                )
                
                assert result['status'] == 'success'
                assert result['execution_mode'] == 'distributed'
                assert 'pdf_result' in result
                assert 'excel_result' in result
                assert 'validation_result' in result
    
    def test_process_validation_request_consolidated(self, temp_files):
        """Test consolidated processing strategy."""
        pdf_path, excel_path = temp_files
        
        # Mock low memory scenario
        with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats, \
             patch('app.autonomous_agents.orchestrator.consolidated_processing_task') as mock_consolidated_task:
            
            mock_stats.return_value = MemoryStats(
                total_gb=8.0,
                available_gb=0.8,
                used_percent=90.0,
                threshold_level=MemoryThreshold.CRITICAL,
                can_spawn_agents=False,
                recommended_agent_count=1
            )
            
            # Mock consolidated task result
            consolidated_result_mock = MagicMock()
            consolidated_result_mock.get.return_value = {
                'status': 'success',
                'mode': 'consolidated',
                'pdf_chunks': 5,
                'excel_rows': 10,
                'validation_result': {'matches': 8, 'mismatches': 2}
            }
            consolidated_result_mock.id = 'consolidated_task_123'
            mock_consolidated_task.delay.return_value = consolidated_result_mock
            
            result = self.orchestrator.process_validation_request(
                pdf_path=pdf_path,
                excel_path=excel_path,
                pdf_filename='test.pdf',
                excel_filename='test.xlsx'
            )
            
            assert result['status'] == 'success'
            assert result['execution_mode'] == 'consolidated'
            assert 'result' in result
    
    def test_get_system_status(self):
        """Test system status retrieval."""
        with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:
            mock_stats.return_value = MemoryStats(
                total_gb=16.0,
                available_gb=8.0,
                used_percent=50.0,
                threshold_level=MemoryThreshold.HIGH,
                can_spawn_agents=True,
                recommended_agent_count=8
            )
            
            status = self.orchestrator.get_system_status()
            
            assert 'memory_stats' in status
            assert 'consolidation_strategy' in status
            assert 'active_tasks' in status
            assert status['consolidation_active'] is False


class TestIntelligentAgents:
    """Test suite for intelligent agent implementations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.pdf_agent = PDFIntelligenceAgent()
        self.excel_agent = ExcelIntelligenceAgent()
        self.validation_agent = ValidationIntelligenceAgent()
        self.consolidated_agent = ConsolidatedProcessingAgent()
    
    def test_pdf_agent_initialization(self):
        """Test PDF agent initialization."""
        assert self.pdf_agent.agent_type == "pdf_intelligence"
        assert len(self.pdf_agent.base_capabilities) == 3
        capability_names = [cap.name for cap in self.pdf_agent.base_capabilities]
        assert "pdf_text_extraction" in capability_names
        assert "pdf_multimodal_processing" in capability_names
        assert "ocr_processing" in capability_names
    
    @patch('app.services.pdf_processor.PDFProcessor')
    def test_pdf_agent_low_memory_processing(self, mock_processor_class):
        """Test PDF agent with low memory using basic processor."""
        mock_processor = Mock()
        mock_processor.process_pdf.return_value = [
            {'text': 'test chunk 1'},
            {'text': 'test chunk 2'}
        ]
        mock_processor_class.return_value = mock_processor
        
        with patch.object(self.pdf_agent.memory_manager, 'get_current_stats') as mock_stats:
            mock_stats.return_value = MemoryStats(
                total_gb=8.0,
                available_gb=1.0,
                used_percent=87.5,
                threshold_level=MemoryThreshold.LOW,
                can_spawn_agents=False,
                recommended_agent_count=2
            )
            
            result = self.pdf_agent.execute_main_logic('/path/to/test.pdf', 'test.pdf')
            
            assert result['status'] == 'success'
            assert result['chunk_count'] == 2
            assert result['processor_type'] == 'basic'
            assert result['filename'] == 'test.pdf'
    
    @patch('app.services.excel_processor.ExcelProcessor')
    def test_excel_agent_processing(self, mock_processor_class):
        """Test Excel agent processing."""
        mock_processor = Mock()
        mock_processor.process_excel.return_value = [
            {'parameter': 'param1', 'value': 'value1'},
            {'parameter': 'param2', 'value': 'value2'}
        ]
        mock_processor_class.return_value = mock_processor
        
        result = self.excel_agent.execute_main_logic('/path/to/test.xlsx', 'test.xlsx')
        
        assert result['status'] == 'success'
        assert result['row_count'] == 2
        assert result['filename'] == 'test.xlsx'
    
    def test_consolidated_agent_initialization(self):
        """Test consolidated agent initialization."""
        assert self.consolidated_agent.agent_type == "consolidated_processing"
        assert len(self.consolidated_agent.base_capabilities) == 3
        capability_names = [cap.name for cap in self.consolidated_agent.base_capabilities]
        assert "pdf_processing" in capability_names
        assert "excel_processing" in capability_names
        assert "validation" in capability_names


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
