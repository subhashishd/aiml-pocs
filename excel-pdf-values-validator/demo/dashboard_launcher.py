#!/usr/bin/env python3
"""
Simple Monitoring Dashboard for Agent System Demo

A simplified dashboard that shows real-time agent system status
without the complex terminal interactions.
"""

import time
import sys
import json
from datetime import datetime
from collections import defaultdict, deque

# Add path for imports
sys.path.append('../fastapi')

from app.autonomous_agents.orchestrator import AdaptiveAgentOrchestrator
from app.autonomous_agents.memory_manager import MemoryManager


class SimpleAgentDashboard:
    """Simple text-based dashboard for agent monitoring."""
    
    def __init__(self):
        self.orchestrator = AdaptiveAgentOrchestrator()
        self.start_time = datetime.now()
        self.update_count = 0
        
    def clear_screen(self):
        """Clear the terminal screen."""
        print('\033[2J\033[H', end='')
    
    def get_system_status(self):
        """Get current system status."""
        try:
            status = self.orchestrator.get_system_status()
            status['timestamp'] = datetime.now().isoformat()
            status['uptime'] = str(datetime.now() - self.start_time).split('.')[0]
            return status
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def format_memory_bar(self, used_percent):
        """Create a simple ASCII memory usage bar."""
        bar_length = 30
        filled = int(bar_length * used_percent / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        if used_percent >= 90:
            color = '\033[91m'  # Red
        elif used_percent >= 70:
            color = '\033[93m'  # Yellow
        else:
            color = '\033[92m'  # Green
        
        return f"{color}{bar}\033[0m {used_percent:.1f}%"
    
    def display_status(self):
        """Display current system status."""
        status = self.get_system_status()
        self.update_count += 1
        
        self.clear_screen()
        
        print("🤖 AUTONOMOUS AGENT SYSTEM - LIVE DASHBOARD")
        print("=" * 60)
        print(f"Uptime: {status.get('uptime', 'Unknown')} | Updates: {self.update_count}")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')} | Status: {'🟢 Online' if 'error' not in status else '🔴 Error'}")
        print()
        
        if 'error' in status:
            print(f"❌ Error: {status['error']}")
            return
        
        # Memory Status
        memory_stats = status.get('memory_stats', {})
        print("📊 MEMORY STATUS")
        print("-" * 40)
        print(f"Available: {memory_stats.get('available_gb', 0):.1f} GB / {memory_stats.get('total_gb', 0):.1f} GB")
        print(f"Usage: {self.format_memory_bar(memory_stats.get('used_percent', 0))}")
        print(f"Threshold: {memory_stats.get('threshold_level', 'UNKNOWN')}")
        print(f"Can Spawn: {'✅ Yes' if memory_stats.get('can_spawn_agents', False) else '❌ No'}")
        print(f"Recommended Agents: {memory_stats.get('recommended_agent_count', 0)}")
        print()
        
        # Agent Status
        active_tasks = status.get('active_tasks', 0)
        task_types = status.get('task_types', [])
        
        print("🤖 AGENT STATUS")
        print("-" * 40)
        if active_tasks > 0:
            print(f"Active Agents: {active_tasks}")
            task_counts = defaultdict(int)
            for task in task_types:
                task_counts[task] += 1
            
            for task_type, count in task_counts.items():
                print(f"  • {task_type}: {count}")
        else:
            print("Active Agents: 0 (No agents currently running)")
        print()
        
        # Delegation Strategy
        strategy = status.get('consolidation_strategy', {})
        action = strategy.get('recommended_action', 'unknown')
        
        print("🧠 DELEGATION STRATEGY")
        print("-" * 40)
        print(f"Current Strategy: {action.replace('_', ' ').title()}")
        
        if 'agent_consolidation' in strategy:
            print("Agent Configuration:")
            for agent_type, count in strategy['agent_consolidation'].items():
                if isinstance(count, int):
                    print(f"  • {agent_type.replace('_', ' ').title()}: {count}")
                else:
                    print(f"  • {agent_type.replace('_', ' ').title()}: {count}")
        
        if strategy.get('memory_optimizations'):
            print("Memory Optimizations:")
            for opt in strategy['memory_optimizations']:
                print(f"  • {opt.replace('_', ' ').title()}")
        
        print()
        print("⚙️  SYSTEM HEALTH")
        print("-" * 40)
        consolidation_active = status.get('consolidation_active', False)
        print(f"Consolidation Mode: {'🟡 Active' if consolidation_active else '🟢 Normal'}")
        print(f"System Load: {'🟢 Normal' if memory_stats.get('used_percent', 0) < 80 else '🟡 High'}")
        print()
        
        # Controls
        print("-" * 60)
        print("Press Ctrl+C to stop monitoring | Refreshing every 2 seconds...")
    
    def run_continuous(self, refresh_interval=2.0):
        """Run the dashboard continuously."""
        try:
            print("🚀 Starting Agent System Dashboard...")
            print("💡 TIP: Run the demo simulation in another terminal:")
            print("   cd demo && python agent_simulation.py --scenario quick")
            print("\nStarting in 3 seconds...")
            time.sleep(3)
            
            while True:
                self.display_status()
                time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Dashboard stopped by user")
        except Exception as e:
            print(f"\n\n❌ Dashboard error: {e}")


def main():
    """Main entry point."""
    dashboard = SimpleAgentDashboard()
    dashboard.run_continuous()


if __name__ == '__main__':
    main()
