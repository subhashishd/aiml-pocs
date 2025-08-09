"""
Performance and Load Testing for Autonomous Agent System.

Tests agent spawning, delegation, resource management, and system performance
under various load conditions and memory constraints.
"""

import pytest
import asyncio
import time
import threading
import tempfile
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch, MagicMock
from statistics import mean, stdev
import sys
sys.path.append('../fastapi')

from app.autonomous_agents.memory_manager import MemoryManager, MemoryThreshold, MemoryStats
from app.autonomous_agents.orchestrator import AdaptiveAgentOrchestrator
from app.autonomous_agents.metrics import AgentMetrics
from app.autonomous_agents.base_agent import AdaptiveAgentTask, AgentCapability


class TestAgentPerformance:
    """Performance tests for individual agents."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = AdaptiveAgentOrchestrator()
        self.memory_manager = MemoryManager(max_memory_gb=16.0)
        self.metrics = AgentMetrics()
        
    def test_agent_spawn_time(self):
        """Test agent spawning performance."""
        spawn_times = []
        
        for i in range(10):
            start_time = time.time()
            
            # Mock high memory for spawning
            with patch.object(self.memory_manager, 'get_current_stats') as mock_stats:
                mock_stats.return_value = MemoryStats(
                    total_gb=16.0,
                    available_gb=12.0,
                    used_percent=25.0,
                    threshold_level=MemoryThreshold.HIGH,
                    can_spawn_agents=True,
                    recommended_agent_count=8
                )
                
                can_spawn, reason = self.memory_manager.can_spawn_agent('pdf_intelligence')
                
            end_time = time.time()
            spawn_times.append(end_time - start_time)
            
            assert can_spawn is True
        
        avg_spawn_time = mean(spawn_times)
        max_spawn_time = max(spawn_times)
        
        # Performance assertions (should spawn in < 10ms on average)
        assert avg_spawn_time < 0.01, f"Average spawn time too slow: {avg_spawn_time:.4f}s"
        assert max_spawn_time < 0.05, f"Maximum spawn time too slow: {max_spawn_time:.4f}s"
        
        print(f"Agent spawn performance - Avg: {avg_spawn_time*1000:.2f}ms, Max: {max_spawn_time*1000:.2f}ms")
    
    def test_memory_calculation_performance(self):
        """Test memory stats calculation performance."""
        calculation_times = []
        
        for i in range(50):
            start_time = time.time()
            stats = self.memory_manager.get_current_stats()
            end_time = time.time()
            
            calculation_times.append(end_time - start_time)
            assert isinstance(stats, MemoryStats)
        
        avg_time = mean(calculation_times)
        max_time = max(calculation_times)
        
        # Should calculate memory stats in < 5ms on average
        assert avg_time < 0.005, f"Memory calculation too slow: {avg_time:.4f}s"
        assert max_time < 0.02, f"Maximum memory calculation too slow: {max_time:.4f}s"
        
        print(f"Memory calculation performance - Avg: {avg_time*1000:.2f}ms, Max: {max_time*1000:.2f}ms")
    
    def test_consolidation_strategy_performance(self):
        """Test consolidation strategy calculation performance."""
        strategy_times = []
        
        for memory_level in [MemoryThreshold.HIGH, MemoryThreshold.MEDIUM, MemoryThreshold.LOW, MemoryThreshold.CRITICAL]:
            for i in range(20):
                with patch.object(self.memory_manager, 'get_current_stats') as mock_stats:
                    mock_stats.return_value = MemoryStats(
                        total_gb=16.0,
                        available_gb=memory_level.value,
                        used_percent=75.0,
                        threshold_level=memory_level,
                        can_spawn_agents=memory_level != MemoryThreshold.CRITICAL,
                        recommended_agent_count=8 if memory_level == MemoryThreshold.HIGH else 1
                    )
                    
                    start_time = time.time()
                    strategy = self.memory_manager.suggest_consolidation_strategy()
                    end_time = time.time()
                    
                    strategy_times.append(end_time - start_time)
                    assert 'recommended_action' in strategy
        
        avg_time = mean(strategy_times)
        max_time = max(strategy_times)
        
        # Should calculate strategy in < 2ms on average
        assert avg_time < 0.002, f"Strategy calculation too slow: {avg_time:.4f}s"
        
        print(f"Consolidation strategy performance - Avg: {avg_time*1000:.2f}ms, Max: {max_time*1000:.2f}ms")


class TestAgentLoadTesting:
    """Load testing for agent orchestration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = AdaptiveAgentOrchestrator()
    
    def test_concurrent_agent_spawning(self):
        """Test spawning multiple agents concurrently."""
        def spawn_agent(agent_type):
            """Helper function to spawn an agent."""
            with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:
                mock_stats.return_value = MemoryStats(
                    total_gb=32.0,
                    available_gb=16.0,
                    used_percent=50.0,
                    threshold_level=MemoryThreshold.HIGH,
                    can_spawn_agents=True,
                    recommended_agent_count=10
                )
                
                return self.orchestrator.memory_manager.can_spawn_agent(agent_type)
        
        agent_types = ['pdf_intelligence', 'excel_intelligence', 'validation', 'ocr_sub_agent']
        spawn_results = []
        start_time = time.time()
        
        # Use ThreadPoolExecutor to simulate concurrent spawning
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            
            # Submit 32 concurrent spawn requests (8 of each type)
            for i in range(32):
                agent_type = agent_types[i % len(agent_types)]
                future = executor.submit(spawn_agent, agent_type)
                futures.append(future)
            
            # Collect results
            for future in futures:
                can_spawn, reason = future.result()
                spawn_results.append(can_spawn)
        
        end_time = time.time()
        total_time = end_time - start_time
        successful_spawns = sum(spawn_results)
        
        # Performance assertions
        assert successful_spawns >= 20, f"Too few successful spawns: {successful_spawns}/32"
        assert total_time < 2.0, f"Concurrent spawning too slow: {total_time:.2f}s"
        
        print(f"Concurrent spawning - {successful_spawns}/32 successful in {total_time:.2f}s")
    
    def test_memory_pressure_simulation(self):
        """Test system behavior under increasing memory pressure."""
        memory_scenarios = [
            (8.0, MemoryThreshold.HIGH),    # 8GB available
            (4.0, MemoryThreshold.MEDIUM),  # 4GB available  
            (2.0, MemoryThreshold.LOW),     # 2GB available
            (0.5, MemoryThreshold.CRITICAL) # 512MB available
        ]
        
        spawn_success_rates = []
        strategy_transitions = []
        
        for available_gb, threshold in memory_scenarios:
            successful_spawns = 0
            total_attempts = 10
            
            for i in range(total_attempts):
                with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:
                    mock_stats.return_value = MemoryStats(
                        total_gb=16.0,
                        available_gb=available_gb,
                        used_percent=(16.0 - available_gb) / 16.0 * 100,
                        threshold_level=threshold,
                        can_spawn_agents=threshold != MemoryThreshold.CRITICAL,
                        recommended_agent_count=8 if threshold == MemoryThreshold.HIGH else 1
                    )
                    
                    can_spawn, _ = self.orchestrator.memory_manager.can_spawn_agent('pdf_intelligence')
                    strategy = self.orchestrator.memory_manager.suggest_consolidation_strategy()
                    
                    if can_spawn:
                        successful_spawns += 1
                    
                    strategy_transitions.append(strategy['recommended_action'])
            
            success_rate = successful_spawns / total_attempts
            spawn_success_rates.append(success_rate)
            
            print(f"Memory {available_gb:.1f}GB ({threshold.name}): {success_rate*100:.0f}% spawn success")
        
        # Verify expected behavior under memory pressure
        assert spawn_success_rates[0] > 0.8, "High memory should allow most spawns"
        assert spawn_success_rates[-1] == 0.0, "Critical memory should block all spawns"
        assert spawn_success_rates[0] > spawn_success_rates[-1], "Success rate should decrease with memory pressure"
    
    def test_agent_delegation_patterns(self):
        """Test different agent delegation patterns."""
        delegation_patterns = {
            'distributed': {
                'memory_gb': 8.0,
                'threshold': MemoryThreshold.HIGH,
                'expected_agents': ['pdf_intelligence', 'excel_intelligence', 'validation']
            },
            'consolidated': {
                'memory_gb': 1.0,
                'threshold': MemoryThreshold.LOW,
                'expected_agents': ['consolidated_processing']
            },
            'minimal': {
                'memory_gb': 0.3,
                'threshold': MemoryThreshold.CRITICAL,
                'expected_agents': ['orchestrator_only']
            }
        }
        
        pattern_results = {}
        
        for pattern_name, config in delegation_patterns.items():
            with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:
                mock_stats.return_value = MemoryStats(
                    total_gb=16.0,
                    available_gb=config['memory_gb'],
                    used_percent=75.0,
                    threshold_level=config['threshold'],
                    can_spawn_agents=config['threshold'] != MemoryThreshold.CRITICAL,
                    recommended_agent_count=len(config['expected_agents'])
                )
                
                strategy = self.orchestrator.memory_manager.suggest_consolidation_strategy()
                pattern_results[pattern_name] = strategy
                
                print(f"{pattern_name.title()} pattern: {strategy['recommended_action']}")
        
        # Verify delegation patterns
        assert 'spawn_specialized_agents' in pattern_results['distributed']['recommended_action']
        assert 'consolidation' in pattern_results['consolidated']['recommended_action']
        assert 'minimal' in pattern_results['minimal']['recommended_action']


class TestAgentTelemetryPerformance:
    """Performance tests for agent telemetry and metrics."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.metrics = AgentMetrics()
    
    def test_metrics_collection_performance(self):
        """Test metrics collection performance."""
        collection_times = []
        
        for i in range(100):
            start_time = time.time()
            
            # Simulate metric collection
            self.metrics.record_agent_task('pdf_intelligence', 'success', 1.5, 256.0)
            self.metrics.update_system_metrics()
            self.metrics.record_memory_threshold('HIGH')
            
            end_time = time.time()
            collection_times.append(end_time - start_time)
        
        avg_time = mean(collection_times)
        max_time = max(collection_times)
        
        # Metrics collection should be very fast (< 1ms average)
        assert avg_time < 0.001, f"Metrics collection too slow: {avg_time:.4f}s"
        assert max_time < 0.01, f"Maximum metrics collection too slow: {max_time:.4f}s"
        
        print(f"Metrics collection performance - Avg: {avg_time*1000:.2f}ms, Max: {max_time*1000:.2f}ms")
    
    def test_metrics_export_performance(self):
        """Test Prometheus metrics export performance."""
        # Populate some metrics
        for i in range(50):
            self.metrics.record_agent_task('pdf_intelligence', 'success', 1.0 + i*0.1, 256.0 + i*10)
            self.metrics.record_agent_task('excel_intelligence', 'success', 0.5 + i*0.05, 128.0 + i*5)
        
        export_times = []
        
        for i in range(20):
            start_time = time.time()
            metrics_text = self.metrics.get_metrics()
            end_time = time.time()
            
            export_times.append(end_time - start_time)
            assert len(metrics_text) > 0, "Metrics export should return data"
        
        avg_time = mean(export_times)
        max_time = max(export_times)
        
        # Metrics export should be fast (< 5ms average)
        assert avg_time < 0.005, f"Metrics export too slow: {avg_time:.4f}s"
        
        print(f"Metrics export performance - Avg: {avg_time*1000:.2f}ms, Max: {max_time*1000:.2f}ms")


class TestSystemStressTest:
    """System-level stress testing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = AdaptiveAgentOrchestrator()
    
    def test_rapid_memory_fluctuations(self):
        """Test system stability under rapid memory changes."""
        memory_levels = [8.0, 2.0, 6.0, 1.0, 4.0, 0.5, 3.0, 0.8, 5.0, 0.3]
        responses = []
        response_times = []
        
        for memory_gb in memory_levels:
            threshold = MemoryThreshold.HIGH if memory_gb >= 6.0 else \
                       MemoryThreshold.MEDIUM if memory_gb >= 3.0 else \
                       MemoryThreshold.LOW if memory_gb >= 1.0 else \
                       MemoryThreshold.CRITICAL
            
            start_time = time.time()
            
            with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:
                mock_stats.return_value = MemoryStats(
                    total_gb=16.0,
                    available_gb=memory_gb,
                    used_percent=(16.0 - memory_gb) / 16.0 * 100,
                    threshold_level=threshold,
                    can_spawn_agents=threshold != MemoryThreshold.CRITICAL,
                    recommended_agent_count=8 if threshold == MemoryThreshold.HIGH else 1
                )
                
                status = self.orchestrator.get_system_status()
                responses.append(status)
            
            end_time = time.time()
            response_times.append(end_time - start_time)
        
        avg_response_time = mean(response_times)
        max_response_time = max(response_times)
        
        # System should remain responsive under fluctuations
        assert avg_response_time < 0.01, f"System too slow under fluctuations: {avg_response_time:.4f}s"
        assert all('memory_stats' in response for response in responses), "All responses should include memory stats"
        
        print(f"Memory fluctuation handling - Avg response: {avg_response_time*1000:.2f}ms")
    
    @pytest.mark.slow
    def test_long_running_stability(self):
        """Test system stability over extended operation (marked as slow test)."""
        # This test simulates extended operation
        start_time = time.time()
        operations = 0
        errors = 0
        
        # Run for 10 seconds or 1000 operations, whichever comes first
        while time.time() - start_time < 10 and operations < 1000:
            try:
                # Simulate various operations
                with patch.object(self.orchestrator.memory_manager, 'get_current_stats') as mock_stats:
                    # Randomize memory conditions
                    memory_gb = 1.0 + (operations % 10) * 0.7  # Varies from 1.0 to 7.3GB
                    
                    mock_stats.return_value = MemoryStats(
                        total_gb=16.0,
                        available_gb=memory_gb,
                        used_percent=75.0,
                        threshold_level=MemoryThreshold.HIGH if memory_gb > 6 else MemoryThreshold.LOW,
                        can_spawn_agents=memory_gb > 1.0,
                        recommended_agent_count=min(8, int(memory_gb))
                    )
                    
                    # Mix of operations
                    if operations % 3 == 0:
                        self.orchestrator.get_system_status()
                    elif operations % 3 == 1:
                        self.orchestrator.memory_manager.can_spawn_agent('pdf_intelligence')
                    else:
                        self.orchestrator.memory_manager.suggest_consolidation_strategy()
                
                operations += 1
                
            except Exception as e:
                errors += 1
                print(f"Error during operation {operations}: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        ops_per_second = operations / duration
        error_rate = errors / operations if operations > 0 else 0
        
        # Performance and stability assertions
        assert error_rate < 0.01, f"Too many errors: {error_rate*100:.1f}%"
        assert ops_per_second > 50, f"Too slow: {ops_per_second:.1f} ops/sec"
        
        print(f"Stability test - {operations} ops in {duration:.1f}s ({ops_per_second:.1f} ops/sec, {error_rate*100:.2f}% errors)")


@pytest.fixture
def temp_files():
    """Create temporary test files."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
        pdf_file.write(b"test pdf content")
        pdf_path = pdf_file.name
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as excel_file:
        excel_file.write(b"test excel content")
        excel_path = excel_file.name
    
    yield pdf_path, excel_path
    
    # Cleanup
    import os
    try:
        os.unlink(pdf_path)
        os.unlink(excel_path)
    except OSError:
        pass  # Files may have been cleaned up already


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
