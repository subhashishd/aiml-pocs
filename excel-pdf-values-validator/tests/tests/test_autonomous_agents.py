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

from autonomous_agents.memory_manager import MemoryManager, MemoryThreshold, MemoryStats
from autonomous_agents.base_agent import AdaptiveAgentTask, AgentCapability, MemoryConstraintError
from autonomous_agents.orchestrator import AdaptiveAgentOrchestrator
from autonomous_agents.intelligent_agents import (
    PDFIntelligenceAgent, 
    ExcelIntelligenceAgent, 
    ValidationIntelligenceAgent,
    ConsolidatedProcessingAgent
)
from autonomous_agents.memory_monitor import MemoryMonitorService

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
    
    @patch('autonomous_agents.intelligent_agents.pdf_intelligence_task')
    @patch('autonomous_agents.intelligent_agents.excel_intelligence_task')
    @patch('autonomous_agents.intelligent_agents.validation_intelligence_task')
    def test_process_validation_request_distributed(
        self, 
        mock_validation_task, 
        mock_excel_task, 
        mock_pdf_task
    ):
        """Test distributed processing strategy."""
        # Mock high memory scenario
        with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:
            mock_stats.return_value = MemoryStats(
                total_gb=16.0,
                available_gb=8.0,
                used_percent=50.0,
                threshold_level=MemoryThreshold.HIGH,
                can_spawn_agents=True,
                recommended_agent_count=8
            )
            
            # Mock task results
            mock_pdf_task.delay.return_value.get.return_value = {
                'status': 'success',
                'chunks': [{'text': 'test chunk'}],
                'chunk_count': 1
            }
            mock_pdf_task.delay.return_value.id = 'pdf_task_123'
            
            mock_excel_task.delay.return_value.get.return_value = {
                'status': 'success',
                'data': [{'parameter': 'test', 'value': 'value'}],
                'row_count': 1
            }
            mock_excel_task.delay.return_value.id = 'excel_task_456'
            
            mock_validation_task.delay.return_value.get.return_value = {
                'status': 'success',
                'validation_result': {'matches': 1, 'mismatches': 0}
            }
            mock_validation_task.delay.return_value.id = 'validation_task_789'
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.pdf') as pdf_file, \\\n                 tempfile.NamedTemporaryFile(suffix='.xlsx') as excel_file:\n                \n                result = self.orchestrator.process_validation_request(\n                    pdf_path=pdf_file.name,\n                    excel_path=excel_file.name,\n                    pdf_filename='test.pdf',\n                    excel_filename='test.xlsx'\n                )\n                \n                assert result['status'] == 'success'\n                assert result['execution_mode'] == 'distributed'\n                assert 'pdf_result' in result\n                assert 'excel_result' in result\n                assert 'validation_result' in result\n    \n    @patch('autonomous_agents.intelligent_agents.consolidated_processing_task')\n    def test_process_validation_request_consolidated(\n        self, \n        mock_consolidated_task\n    ):\n        \"\"\"Test consolidated processing strategy.\"\"\"\n        # Mock low memory scenario\n        with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:\n            mock_stats.return_value = MemoryStats(\n                total_gb=8.0,\n                available_gb=0.8,\n                used_percent=90.0,\n                threshold_level=MemoryThreshold.CRITICAL,\n                can_spawn_agents=False,\n                recommended_agent_count=1\n            )\n            \n            # Mock consolidated task result\n            mock_consolidated_task.delay.return_value.get.return_value = {\n                'status': 'success',\n                'mode': 'consolidated',\n                'pdf_chunks': 5,\n                'excel_rows': 10,\n                'validation_result': {'matches': 8, 'mismatches': 2}\n            }\n            mock_consolidated_task.delay.return_value.id = 'consolidated_task_123'\n            \n            # Create temporary files\n            with tempfile.NamedTemporaryFile(suffix='.pdf') as pdf_file, \\\n                 tempfile.NamedTemporaryFile(suffix='.xlsx') as excel_file:\n                \n                result = self.orchestrator.process_validation_request(\n                    pdf_path=pdf_file.name,\n                    excel_path=excel_file.name,\n                    pdf_filename='test.pdf',\n                    excel_filename='test.xlsx'\n                )\n                \n                assert result['status'] == 'success'\n                assert result['execution_mode'] == 'consolidated'\n                assert 'result' in result\n    \n    def test_get_system_status(self):\n        \"\"\"Test system status retrieval.\"\"\"\n        with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:\n            mock_stats.return_value = MemoryStats(\n                total_gb=16.0,\n                available_gb=8.0,\n                used_percent=50.0,\n                threshold_level=MemoryThreshold.HIGH,\n                can_spawn_agents=True,\n                recommended_agent_count=8\n            )\n            \n            status = self.orchestrator.get_system_status()\n            \n            assert 'memory_stats' in status\n            assert 'consolidation_strategy' in status\n            assert 'active_tasks' in status\n            assert status['consolidation_active'] is False\n\n\nclass TestIntelligentAgents:\n    \"\"\"Test suite for intelligent agent implementations.\"\"\"\n    \n    def setup_method(self):\n        \"\"\"Set up test fixtures.\"\"\"\n        self.pdf_agent = PDFIntelligenceAgent()\n        self.excel_agent = ExcelIntelligenceAgent()\n        self.validation_agent = ValidationIntelligenceAgent()\n        self.consolidated_agent = ConsolidatedProcessingAgent()\n    \n    def test_pdf_agent_initialization(self):\n        \"\"\"Test PDF agent initialization.\"\"\"\n        assert self.pdf_agent.agent_type == \"pdf_intelligence\"\n        assert len(self.pdf_agent.base_capabilities) == 3\n        capability_names = [cap.name for cap in self.pdf_agent.base_capabilities]\n        assert \"pdf_text_extraction\" in capability_names\n        assert \"pdf_multimodal_processing\" in capability_names\n        assert \"ocr_processing\" in capability_names\n    \n    @patch('services.pdf_processor.PDFProcessor')\n    def test_pdf_agent_low_memory_processing(self, mock_processor_class):\n        \"\"\"Test PDF agent with low memory using basic processor.\"\"\"\n        mock_processor = Mock()\n        mock_processor.process_pdf.return_value = [\n            {'text': 'test chunk 1'},\n            {'text': 'test chunk 2'}\n        ]\n        mock_processor_class.return_value = mock_processor\n        \n        with patch.object(self.pdf_agent.memory_manager, 'get_current_stats') as mock_stats:\n            mock_stats.return_value = MemoryStats(\n                total_gb=8.0,\n                available_gb=1.0,\n                used_percent=87.5,\n                threshold_level=MemoryThreshold.LOW,\n                can_spawn_agents=False,\n                recommended_agent_count=2\n            )\n            \n            result = self.pdf_agent.execute_main_logic('/path/to/test.pdf', 'test.pdf')\n            \n            assert result['status'] == 'success'\n            assert result['chunk_count'] == 2\n            assert result['processor_type'] == 'basic'\n            assert result['filename'] == 'test.pdf'\n    \n    @patch('services.excel_processor.ExcelProcessor')\n    def test_excel_agent_processing(self, mock_processor_class):\n        \"\"\"Test Excel agent processing.\"\"\"\n        mock_processor = Mock()\n        mock_processor.process_excel.return_value = [\n            {'parameter': 'param1', 'value': 'value1'},\n            {'parameter': 'param2', 'value': 'value2'}\n        ]\n        mock_processor_class.return_value = mock_processor\n        \n        result = self.excel_agent.execute_main_logic('/path/to/test.xlsx', 'test.xlsx')\n        \n        assert result['status'] == 'success'\n        assert result['row_count'] == 2\n        assert result['filename'] == 'test.xlsx'\n    \n    def test_consolidated_agent_initialization(self):\n        \"\"\"Test consolidated agent initialization.\"\"\"\n        assert self.consolidated_agent.agent_type == \"consolidated_processing\"\n        assert len(self.consolidated_agent.base_capabilities) == 3\n        capability_names = [cap.name for cap in self.consolidated_agent.base_capabilities]\n        assert \"pdf_processing\" in capability_names\n        assert \"excel_processing\" in capability_names\n        assert \"validation\" in capability_names\n\n\nclass TestMemoryMonitorService:\n    \"\"\"Test suite for MemoryMonitorService.\"\"\"\n    \n    def setup_method(self):\n        \"\"\"Set up test fixtures.\"\"\"\n        self.monitor = MemoryMonitorService()\n    \n    def test_monitor_initialization(self):\n        \"\"\"Test monitor initialization.\"\"\"\n        assert isinstance(self.monitor.memory_manager, MemoryManager)\n        assert self.monitor.check_interval == 30.0  # default value\n        assert self.monitor.warning_threshold == 80.0\n        assert self.monitor.critical_threshold == 90.0\n        assert self.monitor.running is False\n        assert self.monitor.telemetry_data == []\n    \n    @patch('psutil.Process')\n    @patch('psutil.virtual_memory')\n    @patch('psutil.cpu_percent')\n    @patch('psutil.cpu_count')\n    def test_collect_telemetry(\n        self, \n        mock_cpu_count, \n        mock_cpu_percent, \n        mock_virtual_memory, \n        mock_process\n    ):\n        \"\"\"Test telemetry collection.\"\"\"\n        # Mock system info\n        mock_virtual_memory.return_value = Mock(\n            total=16 * 1024**3,\n            available=8 * 1024**3,\n            percent=50.0,\n            used=8 * 1024**3,\n            free=8 * 1024**3\n        )\n        mock_process.return_value.memory_info.return_value = Mock(\n            rss=512 * 1024 * 1024,  # 512MB\n            vms=1024 * 1024 * 1024   # 1GB\n        )\n        mock_process.return_value.memory_percent.return_value = 3.125\n        mock_cpu_percent.return_value = 25.0\n        mock_cpu_count.return_value = 8\n        \n        with patch.object(self.monitor.memory_manager, 'get_current_stats') as mock_stats:\n            mock_stats.return_value = MemoryStats(\n                total_gb=16.0,\n                available_gb=8.0,\n                used_percent=50.0,\n                threshold_level=MemoryThreshold.HIGH,\n                can_spawn_agents=True,\n                recommended_agent_count=8\n            )\n            \n            telemetry = self.monitor.collect_telemetry()\n            \n            assert 'timestamp' in telemetry\n            assert 'memory_stats' in telemetry\n            assert 'process_memory' in telemetry\n            assert 'system_memory' in telemetry\n            assert 'agent_status' in telemetry\n            assert 'cpu_stats' in telemetry\n            \n            assert telemetry['memory_stats']['available_gb'] == 8.0\n            assert telemetry['process_memory']['rss_mb'] == 512.0\n            assert telemetry['cpu_stats']['cpu_percent'] == 25.0\n    \n    def test_check_memory_health_healthy(self):\n        \"\"\"Test memory health check with healthy system.\"\"\"\n        telemetry = {\n            \"system_memory\": {\"percent\": 60.0},\n            \"memory_stats\": {\n                \"threshold_level\": \"HIGH\",\n                \"recommended_agent_count\": 8\n            },\n            \"agent_status\": {\"active_tasks\": 3}\n        }\n        \n        health_status = self.monitor.check_memory_health(telemetry)\n        \n        assert health_status['status'] == 'healthy'\n        assert len(health_status['alerts']) == 0\n        assert len(health_status['actions_required']) == 0\n    \n    def test_check_memory_health_critical(self):\n        \"\"\"Test memory health check with critical memory usage.\"\"\"\n        telemetry = {\n            \"system_memory\": {\"percent\": 95.0},\n            \"memory_stats\": {\n                \"threshold_level\": \"CRITICAL\",\n                \"recommended_agent_count\": 1\n            },\n            \"agent_status\": {\"active_tasks\": 1}\n        }\n        \n        health_status = self.monitor.check_memory_health(telemetry)\n        \n        assert health_status['status'] == 'critical'\n        assert len(health_status['alerts']) > 0\n        assert 'force_consolidation' in health_status['actions_required']\n        assert 'aggressive_garbage_collection' in health_status['actions_required']\n    \n    def test_execute_memory_actions(self):\n        \"\"\"Test memory action execution.\"\"\"\n        actions = ['aggressive_garbage_collection', 'suggest_consolidation']\n        \n        with patch('gc.collect', return_value=42):\n            results = self.monitor.execute_memory_actions(actions)\n            \n            assert 'aggressive_garbage_collection' in results\n            assert results['aggressive_garbage_collection']['status'] == 'completed'\n            assert results['aggressive_garbage_collection']['objects_collected'] == 42\n            \n            assert 'suggest_consolidation' in results\n            assert results['suggest_consolidation']['status'] == 'suggested'\n    \n    def test_log_telemetry(self):\n        \"\"\"Test telemetry logging.\"\"\"\n        telemetry = {\n            \"memory_stats\": {\n                \"available_gb\": 8.0,\n                \"threshold_level\": \"HIGH\"\n            },\n            \"agent_status\": {\"active_tasks\": 3}\n        }\n        health_status = {\n            \"status\": \"healthy\",\n            \"alerts\": []\n        }\n        \n        self.monitor.log_telemetry(telemetry, health_status)\n        \n        assert len(self.monitor.telemetry_data) == 1\n        assert self.monitor.telemetry_data[0]['telemetry'] == telemetry\n        assert self.monitor.telemetry_data[0]['health_status'] == health_status\n    \n    def test_get_recent_telemetry(self):\n        \"\"\"Test recent telemetry retrieval.\"\"\"\n        # Add some test data\n        for i in range(15):\n            self.monitor.telemetry_data.append({f\"data_{i}\": i})\n        \n        recent = self.monitor.get_recent_telemetry(limit=5)\n        assert len(recent) == 5\n        assert recent[-1][\"data_14\"] == 14  # Most recent\n        \n        # Test empty case\n        empty_monitor = MemoryMonitorService()\n        recent_empty = empty_monitor.get_recent_telemetry()\n        assert recent_empty == []\n\n\nclass TestIntegration:\n    \"\"\"Integration tests for the complete autonomous agent system.\"\"\"\n    \n    @pytest.mark.asyncio\n    async def test_end_to_end_validation_flow(self):\n        \"\"\"Test complete validation flow using autonomous agents.\"\"\"\n        orchestrator = AdaptiveAgentOrchestrator()\n        \n        # Create temporary test files\n        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as pdf_file:\n            pdf_file.write(\"test pdf content\")\n            pdf_path = pdf_file.name\n        \n        with tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False) as excel_file:\n            excel_file.write(\"test excel content\")\n            excel_path = excel_file.name\n        \n        try:\n            # Mock all the processing components\n            with patch('autonomous_agents.intelligent_agents.pdf_intelligence_task') as mock_pdf, \\\n                 patch('autonomous_agents.intelligent_agents.excel_intelligence_task') as mock_excel, \\\n                 patch('autonomous_agents.intelligent_agents.validation_intelligence_task') as mock_validation:\n                \n                # Mock task results\n                mock_pdf.delay.return_value.get.return_value = {\n                    'status': 'success',\n                    'chunks': [{'text': 'parameter: value'}],\n                    'chunk_count': 1,\n                    'processor_type': 'basic'\n                }\n                mock_pdf.delay.return_value.id = 'pdf_123'\n                \n                mock_excel.delay.return_value.get.return_value = {\n                    'status': 'success',\n                    'data': [{'parameter': 'parameter', 'value': 'value'}],\n                    'row_count': 1\n                }\n                mock_excel.delay.return_value.id = 'excel_456'\n                \n                mock_validation.delay.return_value.get.return_value = {\n                    'status': 'success',\n                    'validation_result': {\n                        'matches': 1,\n                        'mismatches': 0,\n                        'accuracy': 100.0\n                    }\n                }\n                mock_validation.delay.return_value.id = 'validation_789'\n                \n                # Mock high memory scenario for distributed processing\n                with patch.object(orchestrator.memory_manager, 'get_current_stats') as mock_stats:\n                    mock_stats.return_value = MemoryStats(\n                        total_gb=16.0,\n                        available_gb=8.0,\n                        used_percent=50.0,\n                        threshold_level=MemoryThreshold.HIGH,\n                        can_spawn_agents=True,\n                        recommended_agent_count=8\n                    )\n                    \n                    # Execute validation\n                    result = orchestrator.process_validation_request(\n                        pdf_path=pdf_path,\n                        excel_path=excel_path,\n                        pdf_filename='test.pdf',\n                        excel_filename='test.xlsx'\n                    )\n                    \n                    # Verify results\n                    assert result['status'] == 'success'\n                    assert result['execution_mode'] == 'distributed'\n                    assert 'validation_result' in result\n                    assert result['validation_result']['validation_result']['accuracy'] == 100.0\n        \n        finally:\n            # Cleanup\n            os.unlink(pdf_path)\n            os.unlink(excel_path)\n    \n    def test_memory_pressure_adaptation(self):\n        \"\"\"Test system adaptation under memory pressure.\"\"\"\n        memory_manager = MemoryManager()\n        \n        # Simulate increasing memory pressure\n        with patch('psutil.virtual_memory') as mock_memory:\n            # Start with high memory\n            mock_memory.return_value = Mock(\n                total=8 * 1024**3,\n                available=6 * 1024**3,\n                percent=25.0\n            )\n            \n            stats = memory_manager.get_current_stats()\n            strategy = memory_manager.suggest_consolidation_strategy()\n            \n            assert stats.threshold_level == MemoryThreshold.HIGH\n            assert strategy['recommended_action'] == 'spawn_specialized_agents'\n            \n            # Simulate memory pressure increase\n            mock_memory.return_value = Mock(\n                total=8 * 1024**3,\n                available=1.5 * 1024**3,\n                percent=81.25\n            )\n            \n            stats = memory_manager.get_current_stats()\n            strategy = memory_manager.suggest_consolidation_strategy()\n            \n            assert stats.threshold_level == MemoryThreshold.LOW\n            assert strategy['recommended_action'] == 'aggressive_consolidation'\n            assert 'sequential_processing' in strategy['memory_optimizations']\n\n\nif __name__ == '__main__':\n    pytest.main([__file__, '-v'])
