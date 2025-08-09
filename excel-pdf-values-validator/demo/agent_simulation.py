#!/usr/bin/env python3
"""
Agent System Live Demonstration

Simulates realistic agent activity to demonstrate the autonomous agent system
and monitoring dashboard in action.
"""

import asyncio
import time
import random
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# Add path for imports
sys.path.append('../fastapi')

from app.autonomous_agents.orchestrator import AdaptiveAgentOrchestrator
from app.autonomous_agents.memory_manager import MemoryManager, MemoryStats, MemoryThreshold
from app.autonomous_agents.metrics import AgentMetrics, CollectorRegistry


class AgentSimulator:
    """Simulates realistic agent workloads and scenarios."""
    
    def __init__(self):
        self.orchestrator = AdaptiveAgentOrchestrator()
        self.is_running = False
        
        # Create separate metrics registry for simulation
        self.metrics_registry = CollectorRegistry()
        self.metrics = AgentMetrics(registry=self.metrics_registry)
        
        # Simulation statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.start_time = None
        
        # Memory pressure simulation
        self.memory_pressure_level = 0  # 0=normal, 1=medium, 2=high
        
    def simulate_memory_pressure(self, pressure_level: int):
        """Simulate different memory pressure scenarios."""
        self.memory_pressure_level = pressure_level
        
        # Mock memory stats based on pressure level
        if pressure_level == 0:  # Normal
            available_gb = random.uniform(6.0, 12.0)
            threshold = MemoryThreshold.HIGH
        elif pressure_level == 1:  # Medium pressure
            available_gb = random.uniform(2.0, 4.0)
            threshold = MemoryThreshold.MEDIUM
        else:  # High pressure
            available_gb = random.uniform(0.5, 1.5)
            threshold = MemoryThreshold.LOW
        
        return MemoryStats(
            total_gb=16.0,
            available_gb=available_gb,
            used_percent=(16.0 - available_gb) / 16.0 * 100,
            threshold_level=threshold,
            can_spawn_agents=threshold != MemoryThreshold.CRITICAL,
            recommended_agent_count=8 if threshold == MemoryThreshold.HIGH else 3 if threshold == MemoryThreshold.MEDIUM else 1
        )
    
    def simulate_validation_request(self, request_id: str) -> dict:
        """Simulate a single validation request."""
        start_time = time.time()
        
        try:
            # Mock memory stats based on current pressure
            mock_stats = self.simulate_memory_pressure(self.memory_pressure_level)
            
            # Simulate different outcomes based on memory pressure
            if mock_stats.threshold_level == MemoryThreshold.HIGH:
                # High memory - distributed processing
                execution_mode = "distributed"
                processing_time = random.uniform(1.0, 3.0)
                success_rate = 0.95
                
                # Simulate agent activities
                pdf_chunks = random.randint(5, 25)
                excel_rows = random.randint(10, 50)
                accuracy = random.uniform(85.0, 99.0)
                
                # Record metrics
                self.metrics.record_agent_task('pdf_intelligence', 'success', processing_time * 0.4, random.uniform(400, 600))
                self.metrics.record_agent_task('excel_intelligence', 'success', processing_time * 0.2, random.uniform(100, 200))
                self.metrics.record_agent_task('validation_intelligence', 'success', processing_time * 0.4, random.uniform(200, 400))
                
            elif mock_stats.threshold_level == MemoryThreshold.MEDIUM:
                # Medium memory - moderate consolidation
                execution_mode = "moderate_consolidation"
                processing_time = random.uniform(2.0, 5.0)
                success_rate = 0.85
                
                pdf_chunks = random.randint(3, 15)
                excel_rows = random.randint(5, 30)
                accuracy = random.uniform(75.0, 90.0)
                
                # Record consolidated metrics
                self.metrics.record_agent_task('document_processing', 'success', processing_time * 0.6, random.uniform(500, 800))
                self.metrics.record_agent_task('validation_intelligence', 'success', processing_time * 0.4, random.uniform(200, 400))
                
            else:
                # Low memory - aggressive consolidation
                execution_mode = "consolidated"
                processing_time = random.uniform(3.0, 8.0)
                success_rate = 0.75
                
                pdf_chunks = random.randint(2, 10)
                excel_rows = random.randint(3, 20)
                accuracy = random.uniform(60.0, 80.0)
                
                # Record consolidated metrics
                self.metrics.record_agent_task('consolidated_processing', 'success', processing_time, random.uniform(600, 1000))
            
            # Simulate success/failure
            is_success = random.random() < success_rate
            
            if is_success:
                self.successful_requests += 1
                status = "success"
                
                # Record performance metrics
                self.metrics.record_pdf_processing(pdf_chunks)
                self.metrics.record_excel_processing(excel_rows)
                self.metrics.record_validation_result(accuracy)
                
                result = {
                    "request_id": request_id,
                    "status": status,
                    "execution_mode": execution_mode,
                    "processing_time": processing_time,
                    "pdf_chunks": pdf_chunks,
                    "excel_rows": excel_rows,
                    "accuracy": accuracy,
                    "memory_stats": {
                        "available_gb": mock_stats.available_gb,
                        "threshold_level": mock_stats.threshold_level.name
                    }
                }
            else:
                self.failed_requests += 1
                status = "failed"
                error_type = random.choice(['memory_error', 'processing_error', 'validation_error'])
                
                # Record failure
                self.metrics.record_task_failure('validation_request', error_type)
                
                result = {
                    "request_id": request_id,
                    "status": status,
                    "error": error_type,
                    "processing_time": processing_time,
                    "execution_mode": execution_mode
                }
            
            # Update system metrics
            self.metrics.update_system_metrics()
            self.metrics.record_memory_threshold(mock_stats.threshold_level.name)
            self.metrics.record_processing_mode(execution_mode)
            
            # Simulate agent registration/unregistration
            if execution_mode == "distributed":
                active_agents = {'pdf_intelligence': 1, 'excel_intelligence': 1, 'validation_intelligence': 1}
            elif execution_mode == "moderate_consolidation":
                active_agents = {'document_processing': 1, 'validation_intelligence': 1}
            else:
                active_agents = {'consolidated_processing': 1}
            
            self.metrics.update_agent_metrics(active_agents)
            
            return result
            
        except Exception as e:
            self.failed_requests += 1
            self.metrics.record_task_failure('validation_request', 'simulation_error')
            return {
                "request_id": request_id,
                "status": "failed",
                "error": str(e),
                "processing_time": time.time() - start_time
            }
        
        finally:\n            self.total_requests += 1\n    \n    def simulate_concurrent_load(self, num_requests: int = 5):\n        \"\"\"Simulate concurrent validation requests.\"\"\"\n        print(f\"🚀 Simulating {num_requests} concurrent requests...\")\n        \n        with ThreadPoolExecutor(max_workers=num_requests) as executor:\n            futures = []\n            \n            for i in range(num_requests):\n                request_id = f\"req_{int(time.time())}_{i}\"\n                future = executor.submit(self.simulate_validation_request, request_id)\n                futures.append((request_id, future))\n            \n            results = []\n            for request_id, future in futures:\n                try:\n                    result = future.result(timeout=10)\n                    results.append(result)\n                    \n                    status_icon = \"✅\" if result['status'] == 'success' else \"❌\"\n                    if result['status'] == 'success':\n                        print(f\"  {status_icon} {request_id}: {result['execution_mode']} - {result['processing_time']:.1f}s - {result['accuracy']:.1f}% accuracy\")\n                    else:\n                        print(f\"  {status_icon} {request_id}: {result.get('error', 'unknown error')}\")\n                        \n                except Exception as e:\n                    print(f\"  ❌ {request_id}: timeout or error - {e}\")\n                    results.append({\"request_id\": request_id, \"status\": \"timeout\", \"error\": str(e)})\n        \n        return results\n    \n    def simulate_memory_scenario(self, scenario_name: str, duration: int = 30):\n        \"\"\"Simulate specific memory scenarios.\"\"\"\n        print(f\"\\n📊 Running scenario: {scenario_name}\")\n        print(f\"Duration: {duration} seconds\")\n        print(\"─\" * 50)\n        \n        scenario_configs = {\n            \"high_memory_burst\": {\n                \"pressure_levels\": [0, 0, 0, 1, 0, 0, 0],  # Mostly high memory with brief medium pressure\n                \"request_frequency\": 0.5  # Every 0.5 seconds\n            },\n            \"memory_pressure_spike\": {\n                \"pressure_levels\": [0, 1, 2, 2, 1, 0, 0],  # Escalating then recovering\n                \"request_frequency\": 1.0  # Every 1 second\n            },\n            \"sustained_low_memory\": {\n                \"pressure_levels\": [1, 2, 2, 2, 2, 2, 1],  # Sustained pressure\n                \"request_frequency\": 2.0  # Every 2 seconds\n            }\n        }\n        \n        config = scenario_configs.get(scenario_name, scenario_configs[\"high_memory_burst\"])\n        pressure_levels = config[\"pressure_levels\"]\n        request_freq = config[\"request_frequency\"]\n        \n        start_time = time.time()\n        scenario_results = []\n        \n        while (time.time() - start_time) < duration:\n            # Cycle through pressure levels\n            elapsed_ratio = (time.time() - start_time) / duration\n            pressure_index = int(elapsed_ratio * len(pressure_levels))\n            if pressure_index >= len(pressure_levels):\n                pressure_index = len(pressure_levels) - 1\n            \n            self.memory_pressure_level = pressure_levels[pressure_index]\n            \n            # Generate requests based on frequency\n            num_requests = random.randint(1, 3) if pressure_index < 2 else 1\n            results = self.simulate_concurrent_load(num_requests)\n            scenario_results.extend(results)\n            \n            time.sleep(request_freq)\n        \n        # Scenario summary\n        successful = sum(1 for r in scenario_results if r.get('status') == 'success')\n        total = len(scenario_results)\n        success_rate = (successful / total * 100) if total > 0 else 0\n        \n        print(f\"\\n📈 Scenario '{scenario_name}' completed:\")\n        print(f\"  Total requests: {total}\")\n        print(f\"  Successful: {successful} ({success_rate:.1f}%)\")\n        print(f\"  Failed: {total - successful}\")\n        \n        return scenario_results\n    \n    async def run_continuous_simulation(self, duration: int = 300):\n        \"\"\"Run continuous simulation with varying scenarios.\"\"\"\n        print(f\"🎬 Starting continuous agent simulation for {duration} seconds\")\n        print(f\"Start time: {datetime.now().strftime('%H:%M:%S')}\")\n        print(\"=\" * 60)\n        \n        self.is_running = True\n        self.start_time = time.time()\n        \n        scenarios = [\n            (\"high_memory_burst\", 60),\n            (\"memory_pressure_spike\", 90),\n            (\"sustained_low_memory\", 90),\n            (\"high_memory_burst\", 60)  # Recovery phase\n        ]\n        \n        for scenario_name, scenario_duration in scenarios:\n            if not self.is_running:\n                break\n                \n            self.simulate_memory_scenario(scenario_name, scenario_duration)\n            \n            # Brief pause between scenarios\n            if self.is_running:\n                print(\"\\n⏸️  Brief pause between scenarios...\")\n                await asyncio.sleep(5)\n        \n        # Final statistics\n        total_time = time.time() - self.start_time\n        requests_per_min = (self.total_requests / (total_time / 60)) if total_time > 0 else 0\n        success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0\n        \n        print(\"\\n\" + \"=\" * 60)\n        print(\"🏁 SIMULATION COMPLETE\")\n        print(f\"Total duration: {total_time:.1f} seconds\")\n        print(f\"Total requests: {self.total_requests}\")\n        print(f\"Success rate: {success_rate:.1f}%\")\n        print(f\"Requests per minute: {requests_per_min:.1f}\")\n        print(f\"End time: {datetime.now().strftime('%H:%M:%S')}\")\n        \n        self.is_running = False\n    \n    def stop_simulation(self):\n        \"\"\"Stop the simulation gracefully.\"\"\"\n        print(\"\\n🛑 Stopping simulation...\")\n        self.is_running = False\n\n\nasync def main():\n    \"\"\"Main demonstration entry point.\"\"\"\n    import argparse\n    \n    parser = argparse.ArgumentParser(description='Agent System Live Demo')\n    parser.add_argument('--scenario', choices=['quick', 'full', 'custom'], \n                       default='quick', help='Demo scenario to run')\n    parser.add_argument('--duration', type=int, default=120, \n                       help='Duration in seconds (for custom scenario)')\n    \n    args = parser.parse_args()\n    \n    simulator = AgentSimulator()\n    \n    print(\"🤖 AUTONOMOUS AGENT SYSTEM DEMO\")\n    print(\"=\" * 50)\n    print(\"This demo simulates realistic agent workloads to demonstrate:\")\n    print(\"• Dynamic agent delegation based on memory pressure\")\n    print(\"• Resource-aware processing strategies\")\n    print(\"• Performance monitoring and metrics collection\")\n    print(\"• System adaptation under varying load conditions\")\n    print(\"\\n💡 TIP: Run the monitoring dashboard in another terminal:\")\n    print(\"   cd fastapi && python ../tests/monitoring/agent_dashboard.py --mode continuous\")\n    print(\"\\n\" + \"=\" * 50)\n    \n    try:\n        if args.scenario == 'quick':\n            print(\"\\n🚀 Running quick demo (2 minutes)...\")\n            await simulator.run_continuous_simulation(120)\n        elif args.scenario == 'full':\n            print(\"\\n🚀 Running full demo (5 minutes)...\")\n            await simulator.run_continuous_simulation(300)\n        else:\n            print(f\"\\n🚀 Running custom demo ({args.duration} seconds)...\")\n            await simulator.run_continuous_simulation(args.duration)\n            \n    except KeyboardInterrupt:\n        simulator.stop_simulation()\n        print(\"\\n👋 Demo interrupted by user\")\n    \n    except Exception as e:\n        print(f\"\\n❌ Demo error: {e}\")\n    \n    print(\"\\n✨ Demo completed. Check the monitoring dashboard for detailed metrics!\")\n\n\nif __name__ == '__main__':\n    asyncio.run(main())\n"
