#!/usr/bin/env python3
"""
Real-time Agent System Dashboard

Provides a comprehensive dashboard for monitoring agent performance,
resource utilization, delegation patterns, and system health.
"""

import asyncio
import time
import sys
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional
import argparse

# Add paths for imports
sys.path.append('../fastapi')

from app.autonomous_agents.orchestrator import AdaptiveAgentOrchestrator
from app.autonomous_agents.memory_manager import MemoryManager, MemoryThreshold
from app.autonomous_agents.metrics import AgentMetrics


class AgentSystemDashboard:
    """Real-time dashboard for monitoring the autonomous agent system."""
    
    def __init__(self, refresh_interval: float = 2.0):
        """
        Initialize the dashboard.
        
        Args:
            refresh_interval: How often to refresh the display (seconds)
        """
        self.refresh_interval = refresh_interval
        self.orchestrator = AdaptiveAgentOrchestrator()
        self.metrics = AgentMetrics()
        
        # Historical data storage (keep last 100 data points)
        self.history_size = 100
        self.memory_history = deque(maxlen=self.history_size)
        self.agent_history = deque(maxlen=self.history_size)
        self.performance_history = deque(maxlen=self.history_size)
        
        # Statistics tracking
        self.start_time = datetime.now()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.delegation_counts = defaultdict(int)
        
    def clear_screen(self):
        """Clear the terminal screen."""
        print('\033[2J\033[H', end='')
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            status = self.orchestrator.get_system_status()
            
            # Add timestamp
            status['timestamp'] = datetime.now().isoformat()
            
            # Calculate uptime
            uptime = datetime.now() - self.start_time
            status['uptime_seconds'] = uptime.total_seconds()
            status['uptime_formatted'] = str(uptime).split('.')[0]  # Remove microseconds
            
            # Add performance stats
            success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
            status['performance'] = {
                'total_requests': self.total_requests,
                'successful_requests': self.successful_requests,
                'failed_requests': self.failed_requests,
                'success_rate_percent': round(success_rate, 1),
                'requests_per_minute': self.calculate_requests_per_minute()
            }
            
            return status
            
        except Exception as e:
            return {
                'error': f"Failed to get system status: {e}",
                'timestamp': datetime.now().isoformat()
            }
    
    def calculate_requests_per_minute(self) -> float:
        """Calculate requests per minute based on uptime."""
        uptime_minutes = (datetime.now() - self.start_time).total_seconds() / 60
        if uptime_minutes > 0:
            return round(self.total_requests / uptime_minutes, 2)
        return 0.0
    
    def format_memory_info(self, memory_stats: Dict) -> str:
        """Format memory information for display."""
        if not memory_stats:
            return "Memory info unavailable"
        
        available = memory_stats.get('available_gb', 0)
        total = memory_stats.get('total_gb', 0)
        used_percent = memory_stats.get('used_percent', 0)
        threshold = memory_stats.get('threshold_level', 'UNKNOWN')
        
        # Color coding based on threshold
        if threshold == 'HIGH':
            color = '\033[92m'  # Green
        elif threshold == 'MEDIUM':
            color = '\033[93m'  # Yellow
        elif threshold == 'LOW':
            color = '\033[91m'  # Red
        else:
            color = '\033[95m'  # Magenta for critical
        
        reset = '\033[0m'
        
        return f"{color}{available:.1f}GB/{total:.1f}GB ({used_percent:.1f}%) - {threshold}{reset}"
    
    def format_agent_info(self, active_tasks: int, task_types: List[str]) -> str:
        """Format active agent information."""
        if active_tasks == 0:
            return "\033[90mNo active agents\033[0m"  # Gray
        
        # Group task types and count
        task_counts = defaultdict(int)
        for task_type in task_types:
            task_counts[task_type] += 1
        
        agent_str = f"\033[94m{active_tasks} active agents\033[0m: "  # Blue
        agent_details = []
        
        for task_type, count in task_counts.items():
            if count > 1:
                agent_details.append(f"{task_type}({count})")
            else:
                agent_details.append(task_type)
        
        return agent_str + ", ".join(agent_details)
    
    def format_delegation_strategy(self, strategy: Dict) -> str:
        """Format delegation strategy information."""
        action = strategy.get('recommended_action', 'unknown')
        
        strategy_colors = {
            'spawn_specialized_agents': '\033[92m',  # Green
            'moderate_consolidation': '\033[93m',    # Yellow
            'aggressive_consolidation': '\033[91m',  # Red
            'minimal_mode': '\033[95m'              # Magenta
        }
        
        color = strategy_colors.get(action, '\033[0m')
        reset = '\033[0m'
        
        return f"{color}{action.replace('_', ' ').title()}{reset}"
    
    def format_performance_metrics(self, perf: Dict) -> List[str]:
        """Format performance metrics for display."""
        lines = []
        
        success_rate = perf.get('success_rate_percent', 0)
        if success_rate >= 95:
            rate_color = '\033[92m'  # Green
        elif success_rate >= 80:
            rate_color = '\033[93m'  # Yellow
        else:
            rate_color = '\033[91m'  # Red
        
        lines.append(f"Total Requests: {perf.get('total_requests', 0)}")
        lines.append(f"Success Rate: {rate_color}{success_rate}%\033[0m")
        lines.append(f"Requests/Min: {perf.get('requests_per_minute', 0)}")
        
        return lines
    
    def create_memory_graph(self) -> List[str]:
        """Create a simple ASCII graph of memory usage."""
        if len(self.memory_history) < 2:
            return ["Insufficient data for graph"]
        
        lines = []
        graph_width = 50
        graph_height = 8
        
        # Get memory percentages from history
        memory_data = [point.get('used_percent', 0) for point in self.memory_history]
        
        if not memory_data:
            return ["No memory data available"]
        
        # Scale data to graph dimensions
        max_val = max(memory_data) if memory_data else 100
        min_val = min(memory_data) if memory_data else 0
        
        # Create graph
        lines.append("Memory Usage Trend (%):")
        lines.append("├" + "─" * graph_width + "┤")
        
        for row in range(graph_height - 1, -1, -1):
            line = "│"
            threshold = min_val + (max_val - min_val) * row / (graph_height - 1)
            
            # Sample data points across graph width
            for col in range(graph_width):
                if len(memory_data) > 1:
                    idx = int(col * (len(memory_data) - 1) / (graph_width - 1))
                    value = memory_data[idx]
                    
                    if value >= threshold:
                        if value >= 90:
                            line += "\033[91m█\033[0m"  # Red for high usage
                        elif value >= 70:
                            line += "\033[93m█\033[0m"  # Yellow for medium usage
                        else:
                            line += "\033[92m█\033[0m"  # Green for low usage
                    else:
                        line += " "
                else:
                    line += " "
            
            line += f"│ {threshold:3.0f}%"
            lines.append(line)
        
        lines.append("└" + "─" * graph_width + "┘")
        
        return lines
    
    def display_dashboard(self):
        """Display the main dashboard."""
        status = self.get_system_status()
        
        # Store historical data
        if 'memory_stats' in status:
            self.memory_history.append(status['memory_stats'])
        
        if 'active_tasks' in status:
            self.agent_history.append({
                'timestamp': status['timestamp'],
                'active_tasks': status['active_tasks'],
                'task_types': status.get('task_types', [])
            })
        
        self.clear_screen()
        
        # Header
        print("\033[1m" + "="*80)
        print("   AUTONOMOUS AGENT SYSTEM DASHBOARD")
        print("="*80 + "\033[0m")
        print()
        
        # System Overview
        print("\033[1mSYSTEM OVERVIEW\033[0m")
        print("─" * 40)
        print(f"Uptime: {status.get('uptime_formatted', 'Unknown')}")
        print(f"Status: \033[92mOnline\033[0m" if 'error' not in status else f"Status: \033[91m{status['error']}\033[0m")
        print(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        if 'error' in status:
            print(f"\033[91mError: {status['error']}\033[0m")
            return
        
        # Memory Information
        print("\033[1mMEMORY STATUS\033[0m")
        print("─" * 40)
        memory_info = self.format_memory_info(status.get('memory_stats', {}))
        print(f"Memory: {memory_info}")
        print(f"Can Spawn Agents: {'✓' if status.get('memory_stats', {}).get('can_spawn_agents', False) else '✗'}")
        print(f"Recommended Agents: {status.get('memory_stats', {}).get('recommended_agent_count', 0)}")
        print()
        
        # Agent Information
        print("\033[1mAGENT STATUS\033[0m")
        print("─" * 40)
        agent_info = self.format_agent_info(
            status.get('active_tasks', 0),
            status.get('task_types', [])
        )
        print(f"Active Agents: {agent_info}")
        
        strategy_info = self.format_delegation_strategy(status.get('consolidation_strategy', {}))
        print(f"Strategy: {strategy_info}")
        print(f"Consolidation Active: {'Yes' if status.get('consolidation_active', False) else 'No'}")
        print()
        
        # Performance Metrics
        if 'performance' in status:
            print("\033[1mPERFORMANCE METRICS\033[0m")
            print("─" * 40)
            for line in self.format_performance_metrics(status['performance']):
                print(line)
            print()
        
        # Memory Usage Graph
        if len(self.memory_history) > 1:
            print("\033[1mMEMORY TREND\033[0m")
            print("─" * 40)
            for line in self.create_memory_graph():
                print(line)
            print()
        
        # Controls
        print("\033[90m" + "─" * 80)
        print("Controls: [q] Quit | [r] Reset Stats | [s] Save Report")
        print("Refreshing every {:.1f}s...".format(self.refresh_interval) + "\033[0m")
    
    def generate_report(self) -> str:
        """Generate a detailed system report."""
        status = self.get_system_status()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'system_status': status,
            'historical_data': {
                'memory_history': list(self.memory_history),
                'agent_history': list(self.agent_history),
                'performance_history': list(self.performance_history)
            },
            'statistics': {
                'total_uptime_seconds': status.get('uptime_seconds', 0),
                'delegation_patterns': dict(self.delegation_counts),
                'peak_memory_usage': max((point.get('used_percent', 0) for point in self.memory_history), default=0),
                'avg_memory_usage': sum(point.get('used_percent', 0) for point in self.memory_history) / len(self.memory_history) if self.memory_history else 0
            }
        }
        
        return json.dumps(report, indent=2)
    
    def save_report(self, filename: Optional[str] = None):
        """Save system report to file."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"agent_system_report_{timestamp}.json"
        
        report = self.generate_report()
        
        try:
            with open(filename, 'w') as f:
                f.write(report)
            print(f"\033[92mReport saved to {filename}\033[0m")
        except Exception as e:
            print(f"\033[91mError saving report: {e}\033[0m")
    
    def reset_stats(self):
        """Reset performance statistics."""
        self.start_time = datetime.now()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.delegation_counts.clear()
        self.memory_history.clear()
        self.agent_history.clear()
        self.performance_history.clear()
        print("\033[93mStatistics reset\033[0m")
        time.sleep(1)
    
    async def run_interactive(self):
        """Run the dashboard in interactive mode."""
        import select
        import tty
        import termios
        
        # Set terminal to non-blocking mode
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
        
        try:
            while True:
                self.display_dashboard()
                
                # Check for user input (non-blocking)
                start_time = time.time()
                while time.time() - start_time < self.refresh_interval:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1)
                        
                        if key.lower() == 'q':
                            print("\n\033[92mShutting down dashboard...\033[0m")
                            return
                        elif key.lower() == 'r':
                            self.reset_stats()
                            break
                        elif key.lower() == 's':
                            self.save_report()
                            time.sleep(2)
                            break
                    
                    await asyncio.sleep(0.1)
        
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    def run_once(self):
        """Run the dashboard once and exit."""
        self.display_dashboard()
    
    def run_continuous(self, duration: Optional[float] = None):
        """Run the dashboard continuously for a specified duration."""
        start_time = time.time()
        
        try:
            while True:
                self.display_dashboard()
                
                if duration and (time.time() - start_time) >= duration:
                    break
                
                time.sleep(self.refresh_interval)
        
        except KeyboardInterrupt:
            print("\n\033[92mDashboard stopped\033[0m")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Agent System Dashboard')
    parser.add_argument('--mode', choices=['once', 'continuous', 'interactive'], 
                       default='interactive', help='Dashboard mode')
    parser.add_argument('--interval', type=float, default=2.0, 
                       help='Refresh interval in seconds')
    parser.add_argument('--duration', type=float, 
                       help='Duration to run (continuous mode only)')
    parser.add_argument('--save-report', type=str, 
                       help='Save report to specified file and exit')
    
    args = parser.parse_args()
    
    dashboard = AgentSystemDashboard(refresh_interval=args.interval)
    
    if args.save_report:
        dashboard.save_report(args.save_report)
        return
    
    if args.mode == 'once':
        dashboard.run_once()
    elif args.mode == 'continuous':
        dashboard.run_continuous(args.duration)
    else:  # interactive
        await dashboard.run_interactive()


if __name__ == '__main__':
    asyncio.run(main())
