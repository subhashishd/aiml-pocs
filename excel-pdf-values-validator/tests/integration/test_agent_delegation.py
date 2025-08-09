"""
Integration Tests for Agent Delegation and Orchestration.

Tests the complete agent delegation system including dynamic agent spawning,
capability distribution, resource optimization, and failure handling.
"""

import pytest
import asyncio
import time
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock, call
from concurrent.futures import ThreadPoolExecutor
import sys
sys.path.append('../fastapi')

from app.autonomous_agents.orchestrator import AdaptiveAgentOrchestrator
from app.autonomous_agents.memory_manager import MemoryManager, MemoryThreshold, MemoryStats
from app.autonomous_agents.intelligent_agents import (
    PDFIntelligenceAgent, 
    ExcelIntelligenceAgent, 
    ValidationIntelligenceAgent,
    ConsolidatedProcessingAgent
)
from app.autonomous_agents.base_agent import AgentCapability


class TestAgentDelegationWorkflow:
    """Test complete agent delegation workflows."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = AdaptiveAgentOrchestrator()
        self.sample_pdf_chunks = [
            {'text': 'Temperature: 25°C', 'page': 1},
            {'text': 'Pressure: 101.3 kPa', 'page': 1},
            {'text': 'Flow Rate: 150 L/min', 'page': 2}
        ]
        self.sample_excel_data = [
            {'parameter': 'Temperature', 'value': '25°C', 'row': 1},
            {'parameter': 'Pressure', 'value': '101.3 kPa', 'row': 2},
            {'parameter': 'Flow Rate', 'value': '150 L/min', 'row': 3}
        ]
    
    @patch('app.autonomous_agents.orchestrator.pdf_intelligence_task')
    @patch('app.autonomous_agents.orchestrator.excel_intelligence_task') 
    @patch('app.autonomous_agents.orchestrator.validation_intelligence_task')
    def test_high_memory_distributed_delegation(self, mock_validation, mock_excel, mock_pdf):
        """Test agent delegation in high memory scenario (distributed processing)."""
        # Mock high memory scenario
        with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:
            mock_stats.return_value = MemoryStats(
                total_gb=32.0,
                available_gb=16.0,
                used_percent=50.0,
                threshold_level=MemoryThreshold.HIGH,
                can_spawn_agents=True,
                recommended_agent_count=8
            )
            
            # Mock successful task results
            pdf_result_mock = MagicMock()
            pdf_result_mock.get.return_value = {
                'status': 'success',
                'chunks': self.sample_pdf_chunks,
                'chunk_count': 3,
                'processor_type': 'optimized_multimodal',
                'memory_usage_mb': 512.0
            }
            pdf_result_mock.id = 'pdf_task_123'
            mock_pdf.delay.return_value = pdf_result_mock
            
            excel_result_mock = MagicMock()
            excel_result_mock.get.return_value = {
                'status': 'success',
                'data': self.sample_excel_data,
                'row_count': 3,
                'memory_usage_mb': 128.0
            }
            excel_result_mock.id = 'excel_task_456'
            mock_excel.delay.return_value = excel_result_mock
            
            validation_result_mock = MagicMock()
            validation_result_mock.get.return_value = {
                'status': 'success',
                'validation_result': {
                    'matches': 3,
                    'mismatches': 0,
                    'accuracy': 100.0,
                    'total_comparisons': 3
                },
                'config_id': 'config_789',
                'memory_usage_mb': 256.0
            }
            validation_result_mock.id = 'validation_task_789'
            mock_validation.delay.return_value = validation_result_mock
            
            # Execute validation request
            with tempfile.NamedTemporaryFile(suffix='.pdf') as pdf_file, \
                 tempfile.NamedTemporaryFile(suffix='.xlsx') as excel_file:
                
                result = self.orchestrator.process_validation_request(
                    pdf_path=pdf_file.name,
                    excel_path=excel_file.name,
                    pdf_filename='test.pdf',
                    excel_filename='test.xlsx'
                )
                
                # Verify distributed execution
                assert result['status'] == 'success'
                assert result['execution_mode'] == 'distributed'
                
                # Verify all agents were called
                mock_pdf.delay.assert_called_once()
                mock_excel.delay.assert_called_once() 
                mock_validation.delay.assert_called_once()
                
                # Verify task delegation sequence
                pdf_args = mock_pdf.delay.call_args[0]
                excel_args = mock_excel.delay.call_args[0]
                validation_args = mock_validation.delay.call_args[0]
                
                assert pdf_args[1] == 'test.pdf'  # filename
                assert excel_args[1] == 'test.xlsx'  # filename
                assert validation_args[0] == self.sample_pdf_chunks  # pdf chunks
                assert validation_args[1] == self.sample_excel_data  # excel data
                
                # Verify results aggregation
                assert result['pdf_result']['chunk_count'] == 3
                assert result['excel_result']['row_count'] == 3
                assert result['validation_result']['validation_result']['accuracy'] == 100.0
                
                print(f"✓ Distributed delegation successful: 3 agents, 100% accuracy")
    
    @patch('app.autonomous_agents.orchestrator.consolidated_processing_task')
    def test_low_memory_consolidated_delegation(self, mock_consolidated):
        """Test agent delegation in low memory scenario (consolidated processing)."""
        # Mock low memory scenario
        with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:
            mock_stats.return_value = MemoryStats(
                total_gb=8.0,
                available_gb=0.8,
                used_percent=90.0,
                threshold_level=MemoryThreshold.CRITICAL,
                can_spawn_agents=False,
                recommended_agent_count=1
            )
            
            # Mock consolidated processing result
            consolidated_result_mock = MagicMock()
            consolidated_result_mock.get.return_value = {
                'status': 'success',
                'mode': 'consolidated',
                'pdf_chunks': 3,
                'excel_rows': 3,
                'validation_result': {
                    'matches': 2,
                    'mismatches': 1,
                    'accuracy': 66.7
                },
                'config_id': 'config_consolidated_123',
                'memory_usage_mb': 384.0
            }
            consolidated_result_mock.id = 'consolidated_task_456'
            mock_consolidated.delay.return_value = consolidated_result_mock
            
            # Execute validation request
            with tempfile.NamedTemporaryFile(suffix='.pdf') as pdf_file, \
                 tempfile.NamedTemporaryFile(suffix='.xlsx') as excel_file:
                
                result = self.orchestrator.process_validation_request(
                    pdf_path=pdf_file.name,
                    excel_path=excel_file.name,
                    pdf_filename='test.pdf',
                    excel_filename='test.xlsx'
                )
                
                # Verify consolidated execution
                assert result['status'] == 'success'
                assert result['execution_mode'] == 'consolidated'
                
                # Verify single consolidated agent was called
                mock_consolidated.delay.assert_called_once()
                
                # Verify consolidated processing arguments
                args = mock_consolidated.delay.call_args[0]
                assert args[2] == 'test.pdf'  # pdf_filename
                assert args[3] == 'test.xlsx'  # excel_filename
                
                # Verify memory optimization
                assert result['result']['memory_usage_mb'] == 384.0
                
                print(f"✓ Consolidated delegation successful: 1 agent, 66.7% accuracy, 384MB memory")
    
    def test_dynamic_delegation_adaptation(self):
        """Test dynamic adaptation of delegation strategy based on memory changes."""
        memory_scenarios = [
            (12.0, MemoryThreshold.HIGH, 'distributed'),
            (4.0, MemoryThreshold.MEDIUM, 'moderate_consolidation'),
            (1.5, MemoryThreshold.LOW, 'aggressive_consolidation'),
            (0.4, MemoryThreshold.CRITICAL, 'minimal_mode')
        ]
        
        delegation_decisions = []
        
        for memory_gb, threshold, expected_mode in memory_scenarios:
            with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:
                mock_stats.return_value = MemoryStats(
                    total_gb=16.0,
                    available_gb=memory_gb,
                    used_percent=(16.0 - memory_gb) / 16.0 * 100,
                    threshold_level=threshold,
                    can_spawn_agents=threshold != MemoryThreshold.CRITICAL,
                    recommended_agent_count=8 if threshold == MemoryThreshold.HIGH else 1
                )
                
                # Check delegation strategy
                strategy = self.orchestrator.memory_manager.suggest_consolidation_strategy()
                delegation_decisions.append((memory_gb, strategy['recommended_action']))
                
                print(f"Memory {memory_gb:.1f}GB → {strategy['recommended_action']}")
        
        # Verify progressive delegation adaptation
        assert 'spawn_specialized_agents' in delegation_decisions[0][1]  # High memory
        assert 'consolidation' in delegation_decisions[2][1]  # Low memory
        assert 'minimal' in delegation_decisions[3][1]  # Critical memory
        
        print("✓ Dynamic delegation adaptation working correctly")
    
    def test_agent_capability_distribution(self):
        """Test how capabilities are distributed across agents."""
        agents = {
            'pdf': PDFIntelligenceAgent(),
            'excel': ExcelIntelligenceAgent(), 
            'validation': ValidationIntelligenceAgent(),
            'consolidated': ConsolidatedProcessingAgent()
        }
        
        capability_distribution = {}
        
        for agent_name, agent in agents.items():
            capabilities = [cap.name for cap in agent.base_capabilities]
            capability_distribution[agent_name] = capabilities
            
            print(f"{agent_name.upper()} Agent capabilities: {capabilities}")
        
        # Verify capability specialization
        assert 'pdf_text_extraction' in capability_distribution['pdf']
        assert 'pdf_multimodal_processing' in capability_distribution['pdf']
        assert 'excel_processing' in capability_distribution['excel']
        assert 'semantic_validation' in capability_distribution['validation']
        
        # Verify consolidated agent has all major capabilities
        consolidated_caps = capability_distribution['consolidated']
        assert 'pdf_processing' in consolidated_caps
        assert 'excel_processing' in consolidated_caps
        assert 'validation' in consolidated_caps
        
        print("✓ Agent capability distribution verified")
    
    def test_agent_failure_delegation_fallback(self):
        """Test delegation fallback when agents fail."""
        with patch('app.autonomous_agents.orchestrator.pdf_intelligence_task') as mock_pdf, \
             patch('app.autonomous_agents.orchestrator.excel_intelligence_task') as mock_excel, \
             patch('app.autonomous_agents.orchestrator.consolidated_processing_task') as mock_consolidated:
            
            # Mock high memory scenario initially
            with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:
                mock_stats.return_value = MemoryStats(
                    total_gb=16.0,
                    available_gb=8.0,
                    used_percent=50.0,
                    threshold_level=MemoryThreshold.HIGH,
                    can_spawn_agents=True,
                    recommended_agent_count=8
                )
                
                # Mock PDF agent failure
                pdf_result_mock = MagicMock()
                pdf_result_mock.get.side_effect = Exception("PDF processing failed")
                pdf_result_mock.id = 'pdf_task_failed'
                mock_pdf.delay.return_value = pdf_result_mock
                
                # Test failure handling
                with tempfile.NamedTemporaryFile(suffix='.pdf') as pdf_file, \
                     tempfile.NamedTemporaryFile(suffix='.xlsx') as excel_file:
                    
                    with pytest.raises(Exception, match="PDF processing failed"):
                        self.orchestrator.process_validation_request(
                            pdf_path=pdf_file.name,
                            excel_path=excel_file.name,
                            pdf_filename='test.pdf',
                            excel_filename='test.xlsx'
                        )
                    
                    # Verify cleanup after failure
                    assert len(self.orchestrator.active_tasks) == 0
                    
                    print("✓ Agent failure handling and cleanup verified")


class TestAgentResourceManagement:
    """Test resource management and optimization."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = AdaptiveAgentOrchestrator()
        self.memory_manager = MemoryManager(max_memory_gb=16.0)
    
    def test_memory_based_agent_selection(self):
        """Test agent selection based on available memory."""
        test_scenarios = [
            {
                'available_gb': 8.0,
                'expected_pdf_processor': 'optimized_multimodal',
                'can_spawn_multiple': True
            },
            {
                'available_gb': 3.0,
                'expected_pdf_processor': 'multimodal',
                'can_spawn_multiple': True
            },
            {
                'available_gb': 1.5,
                'expected_pdf_processor': 'basic',
                'can_spawn_multiple': False
            }
        ]
        
        for scenario in test_scenarios:
            with patch.object(self.memory_manager, 'get_current_stats') as mock_stats:
                threshold = MemoryThreshold.HIGH if scenario['available_gb'] >= 6.0 else \
                           MemoryThreshold.MEDIUM if scenario['available_gb'] >= 3.0 else \
                           MemoryThreshold.LOW
                
                mock_stats.return_value = MemoryStats(
                    total_gb=16.0,
                    available_gb=scenario['available_gb'],
                    used_percent=75.0,
                    threshold_level=threshold,
                    can_spawn_agents=scenario['can_spawn_multiple'],
                    recommended_agent_count=8 if scenario['can_spawn_multiple'] else 2
                )
                
                # Test agent spawning decision
                can_spawn_pdf, _ = self.memory_manager.can_spawn_agent('pdf_intelligence')
                can_spawn_excel, _ = self.memory_manager.can_spawn_agent('excel_intelligence')
                
                if scenario['can_spawn_multiple']:
                    assert can_spawn_pdf, f"PDF agent should spawn with {scenario['available_gb']}GB"
                    assert can_spawn_excel, f"Excel agent should spawn with {scenario['available_gb']}GB"
                
                print(f"Memory {scenario['available_gb']}GB: PDF={can_spawn_pdf}, Excel={can_spawn_excel}")
        
        print("✓ Memory-based agent selection working correctly")
    
    def test_agent_memory_profiling(self):
        """Test agent memory profiling and tracking."""
        agent_profiles = self.memory_manager.AGENT_PROFILES
        
        # Verify memory profiles exist for all agent types
        expected_agents = [
            'orchestrator', 'pdf_intelligence', 'excel_intelligence',
            'validation', 'evaluation', 'ocr_sub_agent', 'multimodal_sub_agent'
        ]
        
        for agent_type in expected_agents:
            assert agent_type in agent_profiles, f"Missing profile for {agent_type}"
            
            profile = agent_profiles[agent_type]
            assert profile.base_memory_mb > 0, f"Invalid base memory for {agent_type}"
            assert profile.peak_memory_mb >= profile.base_memory_mb, f"Peak < base for {agent_type}"
            
            print(f"{agent_type}: Base={profile.base_memory_mb}MB, Peak={profile.peak_memory_mb}MB, Model={profile.model_memory_mb}MB")
        
        # Verify multimodal agents have higher memory requirements
        assert agent_profiles['multimodal_sub_agent'].model_memory_mb > agent_profiles['excel_intelligence'].model_memory_mb
        assert agent_profiles['pdf_intelligence'].model_memory_mb > 0  # BLIP model
        
        print("✓ Agent memory profiling verified")
    
    def test_concurrent_agent_resource_contention(self):
        """Test resource contention when multiple agents compete."""
        def attempt_spawn(agent_type, delay=0):
            """Helper to spawn agent with optional delay using atomic method."""
            if delay:
                time.sleep(delay)
            return self.memory_manager.try_spawn_agent(agent_type)
        
        # Mock moderate memory scenario
        with patch.object(self.memory_manager, 'get_current_stats') as mock_stats:
            mock_stats.return_value = MemoryStats(
                total_gb=16.0,
                available_gb=4.0,  # Moderate memory
                used_percent=75.0,
                threshold_level=MemoryThreshold.MEDIUM,
                can_spawn_agents=True,
                recommended_agent_count=3  # Limited agent count
            )
            
            # Simulate concurrent spawning attempts
            with ThreadPoolExecutor(max_workers=6) as executor:
                futures = []
                
                # Submit spawn requests for different agent types
                agent_requests = [
                    ('pdf_intelligence', 0),
                    ('pdf_intelligence', 0.01),  # Slight delay
                    ('excel_intelligence', 0),
                    ('validation', 0.02),
                    ('ocr_sub_agent', 0),
                    ('multimodal_sub_agent', 0.01)
                ]
                
                for agent_type, delay in agent_requests:
                    future = executor.submit(attempt_spawn, agent_type, delay)
                    futures.append((agent_type, future))
                
                # Collect results
                results = []
                for agent_type, future in futures:
                    can_spawn, reason = future.result()
                    results.append((agent_type, can_spawn, reason))
                    # No need to manually register - try_spawn_agent does it atomically
            
            successful_spawns = sum(1 for _, can_spawn, _ in results)
            
            print(f"Concurrent spawning results ({successful_spawns}/{len(results)} successful):")
            for agent_type, can_spawn, reason in results:
                status = "✓" if can_spawn else "✗"
                print(f"  {status} {agent_type}: {reason}")
            
            # Count actual successes and rejections from the output
            actual_successes = sum(1 for _, can_spawn, _ in results if can_spawn)
            actual_rejections = sum(1 for _, can_spawn, _ in results if not can_spawn)
            rejection_for_limits = sum(1 for _, can_spawn, reason in results if not can_spawn and "limit reached" in reason)
            
            # Verify resource contention handling with atomic operations
            assert actual_successes == 3, f"Should spawn exactly 3 agents with atomic operations, got {actual_successes}"
            assert actual_rejections == 3, f"Should reject exactly 3 agents, got {actual_rejections}"
            assert rejection_for_limits == 3, f"All rejections should be due to limits, got {rejection_for_limits} limit rejections"
            
            print("✓ Resource contention handling verified with atomic operations")


class TestAgentSystemIntegration:
    """End-to-end system integration tests."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = AdaptiveAgentOrchestrator()
    
    def test_full_delegation_workflow_with_metrics(self):
        """Test complete delegation workflow with metrics collection."""
        from app.autonomous_agents.metrics import AgentMetrics
        
        metrics = AgentMetrics()
        
        # Mock full workflow execution
        with patch('app.autonomous_agents.orchestrator.pdf_intelligence_task') as mock_pdf, \
             patch('app.autonomous_agents.orchestrator.excel_intelligence_task') as mock_excel, \
             patch('app.autonomous_agents.orchestrator.validation_intelligence_task') as mock_validation:
            
            # Mock high memory for distributed processing
            with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:
                mock_stats.return_value = MemoryStats(
                    total_gb=32.0,
                    available_gb=20.0,
                    used_percent=37.5,
                    threshold_level=MemoryThreshold.HIGH,
                    can_spawn_agents=True,
                    recommended_agent_count=8
                )
                
                # Mock successful execution with timing
                start_time = time.time()
                
                pdf_result_mock = MagicMock()
                pdf_result_mock.get.return_value = {
                    'status': 'success',
                    'chunks': [{'text': f'chunk_{i}'} for i in range(10)],
                    'chunk_count': 10,
                    'memory_usage_mb': 512.0
                }
                pdf_result_mock.id = 'pdf_metrics_test'
                mock_pdf.delay.return_value = pdf_result_mock
                
                excel_result_mock = MagicMock()
                excel_result_mock.get.return_value = {
                    'status': 'success',
                    'data': [{'parameter': f'param_{i}', 'value': f'val_{i}'} for i in range(15)],
                    'row_count': 15,
                    'memory_usage_mb': 128.0
                }
                excel_result_mock.id = 'excel_metrics_test'
                mock_excel.delay.return_value = excel_result_mock
                
                validation_result_mock = MagicMock()
                validation_result_mock.get.return_value = {
                    'status': 'success',
                    'validation_result': {'matches': 8, 'mismatches': 2, 'accuracy': 80.0},
                    'memory_usage_mb': 256.0
                }
                validation_result_mock.id = 'validation_metrics_test'
                mock_validation.delay.return_value = validation_result_mock
                
                # Execute workflow
                with tempfile.NamedTemporaryFile(suffix='.pdf') as pdf_file, \
                     tempfile.NamedTemporaryFile(suffix='.xlsx') as excel_file:
                    
                    result = self.orchestrator.process_validation_request(
                        pdf_path=pdf_file.name,
                        excel_path=excel_file.name,
                        pdf_filename='metrics_test.pdf',
                        excel_filename='metrics_test.xlsx'
                    )
                
                end_time = time.time()
                workflow_duration = end_time - start_time
                
                # Record metrics
                metrics.record_agent_task('pdf_intelligence', 'success', 1.5, 512.0)
                metrics.record_agent_task('excel_intelligence', 'success', 0.8, 128.0)
                metrics.record_agent_task('validation_intelligence', 'success', 2.1, 256.0)
                metrics.record_pdf_processing(10)
                metrics.record_excel_processing(15)
                metrics.record_validation_result(80.0)
                
                # Verify workflow success
                assert result['status'] == 'success'
                assert result['execution_mode'] == 'distributed'
                
                # Verify metrics collection
                metrics_export = metrics.get_metrics()
                assert len(metrics_export) > 0
                assert 'agent_tasks_total' in metrics_export
                assert 'pdf_processing_chunks_count' in metrics_export
                
                print(f"✓ Full workflow completed in {workflow_duration:.2f}s with metrics")
                print(f"  - PDF: 10 chunks, 512MB")
                print(f"  - Excel: 15 rows, 128MB") 
                print(f"  - Validation: 80% accuracy, 256MB")
    
    def test_system_health_monitoring_integration(self):
        """Test integration with system health monitoring."""
        # Test health monitoring calls
        system_status_calls = []
        
        def mock_health_check():
            status = self.orchestrator.get_system_status()
            system_status_calls.append(status)
            return status
        
        # Simulate periodic health checks
        for i in range(5):
            with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:
                # Vary memory conditions
                memory_gb = 8.0 - i * 1.5  # Decreasing memory
                threshold = MemoryThreshold.HIGH if memory_gb > 6 else \
                           MemoryThreshold.MEDIUM if memory_gb > 3 else \
                           MemoryThreshold.LOW
                
                mock_stats.return_value = MemoryStats(
                    total_gb=16.0,
                    available_gb=memory_gb,
                    used_percent=75.0,
                    threshold_level=threshold,
                    can_spawn_agents=memory_gb > 2.0,
                    recommended_agent_count=max(1, int(memory_gb))
                )
                
                status = mock_health_check()
                print(f"Health check {i+1}: {memory_gb:.1f}GB, {threshold.name}")
        
        # Verify health monitoring data
        assert len(system_status_calls) == 5
        for status in system_status_calls:
            assert 'memory_stats' in status
            assert 'consolidation_strategy' in status
            assert 'active_tasks' in status
        
        # Verify memory trend detection
        memory_levels = [status['memory_stats']['available_gb'] for status in system_status_calls]
        assert memory_levels[0] > memory_levels[-1], "Memory should decrease over time"
        
        print("✓ System health monitoring integration verified")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
