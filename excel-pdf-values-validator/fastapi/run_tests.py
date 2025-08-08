#!/usr/bin/env python3
"""
Test Runner for Autonomous Agent System

Comprehensive test runner that validates the complete autonomous agent
system including unit tests, integration tests, and system health checks.
"""

import os
import sys
import subprocess
import tempfile
import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestRunner:
    """Test runner for autonomous agent system."""
    
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        
    def run_unit_tests(self):
        """Run unit tests using pytest."""
        logger.info("Running unit tests...")
        
        try:
            # Run pytest with coverage
            cmd = [
                sys.executable, '-m', 'pytest', 
                'tests/', 
                '-v', 
                '--tb=short',
                '--disable-warnings'
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            if result.returncode == 0:
                logger.info("✅ Unit tests passed")
                self.test_results.append(("Unit Tests", "PASSED"))
            else:
                logger.error("❌ Unit tests failed")
                logger.error(result.stdout)
                logger.error(result.stderr)
                self.test_results.append(("Unit Tests", "FAILED"))
                self.failed_tests.append("Unit Tests")
                
        except Exception as e:
            logger.error(f"Error running unit tests: {e}")
            self.test_results.append(("Unit Tests", "ERROR"))
            self.failed_tests.append("Unit Tests")
    
    def test_memory_manager(self):
        """Test memory manager functionality."""
        logger.info("Testing memory manager...")
        
        try:
            sys.path.insert(0, 'app')
            from autonomous_agents.memory_manager import MemoryManager
            
            # Test initialization
            manager = MemoryManager(max_memory_gb=8.0)
            assert manager.max_memory_gb == 8.0
            
            # Test stats retrieval
            stats = manager.get_current_stats()
            assert stats.total_gb > 0
            assert stats.available_gb > 0
            
            # Test agent registration
            manager.register_agent('test_agent')
            assert manager.active_agents['test_agent'] == 1
            
            manager.unregister_agent('test_agent')
            assert 'test_agent' not in manager.active_agents
            
            logger.info("✅ Memory manager tests passed")
            self.test_results.append(("Memory Manager", "PASSED"))
            
        except Exception as e:
            logger.error(f"❌ Memory manager tests failed: {e}")
            self.test_results.append(("Memory Manager", "FAILED"))
            self.failed_tests.append("Memory Manager")
    
    def test_orchestrator(self):
        """Test orchestrator functionality."""
        logger.info("Testing orchestrator...")
        
        try:
            sys.path.insert(0, 'app')
            from autonomous_agents.orchestrator import AdaptiveAgentOrchestrator
            
            # Test initialization
            orchestrator = AdaptiveAgentOrchestrator()
            assert hasattr(orchestrator, 'memory_manager')
            assert orchestrator.active_tasks == {}
            
            # Test system status
            status = orchestrator.get_system_status()
            assert 'memory_stats' in status
            assert 'consolidation_strategy' in status
            
            logger.info("✅ Orchestrator tests passed")
            self.test_results.append(("Orchestrator", "PASSED"))
            
        except Exception as e:
            logger.error(f"❌ Orchestrator tests failed: {e}")
            self.test_results.append(("Orchestrator", "FAILED"))
            self.failed_tests.append("Orchestrator")
    
    def test_intelligent_agents(self):
        """Test intelligent agent implementations."""
        logger.info("Testing intelligent agents...")
        
        try:
            sys.path.insert(0, 'app')
            from autonomous_agents.intelligent_agents import (
                PDFIntelligenceAgent,
                ExcelIntelligenceAgent,
                ValidationIntelligenceAgent,
                ConsolidatedProcessingAgent
            )
            
            # Test agent initialization
            pdf_agent = PDFIntelligenceAgent()
            assert pdf_agent.agent_type == "pdf_intelligence"
            assert len(pdf_agent.base_capabilities) > 0
            
            excel_agent = ExcelIntelligenceAgent()
            assert excel_agent.agent_type == "excel_intelligence"
            
            validation_agent = ValidationIntelligenceAgent()
            assert validation_agent.agent_type == "validation_intelligence"
            
            consolidated_agent = ConsolidatedProcessingAgent()
            assert consolidated_agent.agent_type == "consolidated_processing"
            
            logger.info("✅ Intelligent agents tests passed")
            self.test_results.append(("Intelligent Agents", "PASSED"))
            
        except Exception as e:
            logger.error(f"❌ Intelligent agents tests failed: {e}")
            self.test_results.append(("Intelligent Agents", "FAILED"))
            self.failed_tests.append("Intelligent Agents")
    
    def test_memory_monitor(self):
        """Test memory monitor service."""
        logger.info("Testing memory monitor...")
        
        try:
            sys.path.insert(0, 'app')
            from autonomous_agents.memory_monitor import MemoryMonitorService
            
            # Test initialization
            monitor = MemoryMonitorService()
            assert hasattr(monitor, 'memory_manager')
            assert monitor.running is False
            
            # Test telemetry collection
            telemetry = monitor.collect_telemetry()
            assert 'timestamp' in telemetry
            assert 'memory_stats' in telemetry
            
            logger.info("✅ Memory monitor tests passed")
            self.test_results.append(("Memory Monitor", "PASSED"))
            
        except Exception as e:
            logger.error(f"❌ Memory monitor tests failed: {e}")
            self.test_results.append(("Memory Monitor", "FAILED"))
            self.failed_tests.append("Memory Monitor")
    
    def test_fastapi_integration(self):
        """Test FastAPI integration."""
        logger.info("Testing FastAPI integration...")
        
        try:
            sys.path.insert(0, 'app')
            from main_autonomous import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            # Test root endpoint
            response = client.get("/")
            assert response.status_code == 200
            assert "Autonomous" in response.json()["message"]
            
            # Test health endpoint
            response = client.get("/health")
            assert response.status_code in [200, 503]  # May fail if services not running
            
            # Test system status endpoint
            response = client.get("/system-status")
            assert response.status_code == 200
            assert "memory_stats" in response.json()
            
            logger.info("✅ FastAPI integration tests passed")
            self.test_results.append(("FastAPI Integration", "PASSED"))
            
        except Exception as e:
            logger.error(f"❌ FastAPI integration tests failed: {e}")
            self.test_results.append(("FastAPI Integration", "FAILED"))
            self.failed_tests.append("FastAPI Integration")
    
    def test_docker_setup(self):
        """Test Docker configuration."""
        logger.info("Testing Docker setup...")
        
        try:
            # Check if Dockerfile exists
            if not os.path.exists("Dockerfile"):
                raise FileNotFoundError("Dockerfile not found")
            
            # Check if docker-compose.yml exists
            if not os.path.exists("docker-compose.yml"):
                raise FileNotFoundError("docker-compose.yml not found")
            
            # Check if requirements.txt exists
            if not os.path.exists("requirements.txt"):
                raise FileNotFoundError("requirements.txt not found")
            
            logger.info("✅ Docker setup tests passed")
            self.test_results.append(("Docker Setup", "PASSED"))
            
        except Exception as e:
            logger.error(f"❌ Docker setup tests failed: {e}")
            self.test_results.append(("Docker Setup", "FAILED"))
            self.failed_tests.append("Docker Setup")
    
    def test_system_integration(self):
        """Test complete system integration."""
        logger.info("Testing system integration...")
        
        try:
            sys.path.insert(0, 'app')
            from autonomous_agents.orchestrator import orchestrator
            
            # Test system status
            status = orchestrator.get_system_status()
            assert 'memory_stats' in status
            
            # Test memory thresholds
            memory_stats = status['memory_stats']
            assert memory_stats['total_gb'] > 0
            assert memory_stats['available_gb'] > 0
            
            # Test consolidation strategy
            strategy = status['consolidation_strategy']
            assert 'recommended_action' in strategy
            
            logger.info("✅ System integration tests passed")
            self.test_results.append(("System Integration", "PASSED"))
            
        except Exception as e:
            logger.error(f"❌ System integration tests failed: {e}")
            self.test_results.append(("System Integration", "FAILED"))
            self.failed_tests.append("System Integration")
    
    def run_all_tests(self):
        """Run all tests."""
        logger.info("🚀 Starting comprehensive test suite for Autonomous Agent System")
        logger.info("=" * 80)
        
        # Run individual test suites
        self.test_memory_manager()
        self.test_orchestrator()
        self.test_intelligent_agents()
        self.test_memory_monitor()
        self.test_fastapi_integration()
        self.test_docker_setup()
        self.test_system_integration()
        
        # Run unit tests if pytest is available
        try:
            import pytest
            self.run_unit_tests()
        except ImportError:
            logger.warning("pytest not available, skipping unit tests")
            self.test_results.append(("Unit Tests", "SKIPPED"))
        
        # Print results
        self.print_results()
    
    def print_results(self):
        """Print test results summary."""
        logger.info("=" * 80)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r[1] == "PASSED"])
        failed_tests = len([r for r in self.test_results if r[1] == "FAILED"])
        skipped_tests = len([r for r in self.test_results if r[1] == "SKIPPED"])
        
        for test_name, result in self.test_results:
            status_icon = {
                "PASSED": "✅",
                "FAILED": "❌", 
                "SKIPPED": "⏭️",
                "ERROR": "💥"
            }.get(result, "❓")
            
            logger.info(f"{status_icon} {test_name}: {result}")
        
        logger.info("-" * 80)
        logger.info(f"📈 TOTAL: {total_tests} | ✅ PASSED: {passed_tests} | ❌ FAILED: {failed_tests} | ⏭️ SKIPPED: {skipped_tests}")
        
        if failed_tests == 0:
            logger.info("🎉 ALL TESTS PASSED! System is ready for deployment.")
        else:
            logger.warning(f"⚠️  {failed_tests} test(s) failed. Review and fix before deployment.")
            logger.warning(f"Failed tests: {', '.join(self.failed_tests)}")
        
        logger.info("=" * 80)
        
        return failed_tests == 0

def main():
    """Main test runner entry point."""
    runner = TestRunner()
    success = runner.run_all_tests()
    
    if success:
        logger.info("🚀 Ready to run: ./test_docker.sh")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
