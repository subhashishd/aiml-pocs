"""
Advanced Telemetry Analysis and Alerting System.

Provides intelligent analysis of agent telemetry data, trend detection,
anomaly detection, and automated alerting for the autonomous agent system.
"""

import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class TrendDirection(Enum):
    """Trend direction indicators."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class TelemetryAlert:
    """Represents a telemetry-based alert."""
    id: str
    severity: AlertSeverity
    title: str
    description: str
    timestamp: datetime
    metrics: Dict[str, Any]
    recommendations: List[str]
    auto_resolve: bool = False

@dataclass
class TrendAnalysis:
    """Results of trend analysis."""
    metric_name: str
    direction: TrendDirection
    slope: float
    confidence: float
    forecast_24h: Optional[float]
    anomalies_detected: int
    recommendations: List[str]

class TelemetryAnalyzer:
    """
    Advanced telemetry analysis system with intelligent alerting
    and trend detection capabilities.
    """
    
    def __init__(self):
        self.telemetry_history: List[Dict[str, Any]] = []
        self.active_alerts: Dict[str, TelemetryAlert] = {}
        self.alert_history: List[TelemetryAlert] = []
        self.analysis_window = 100  # Number of data points to analyze
        
        # Thresholds for different metrics
        self.thresholds = {
            'memory_usage_critical': 95.0,
            'memory_usage_warning': 85.0,
            'task_failure_rate_critical': 10.0,
            'task_failure_rate_warning': 5.0,
            'avg_task_duration_warning': 300.0,  # 5 minutes
            'avg_task_duration_critical': 600.0,  # 10 minutes
            'agent_spawn_failure_rate': 20.0,
            'consolidation_frequency_high': 5.0,  # per hour
        }
        
        logger.info("Telemetry analyzer initialized")
    
    def add_telemetry_data(self, telemetry: Dict[str, Any]) -> None:
        """Add new telemetry data point for analysis."""
        try:
            # Add timestamp if not present
            if 'timestamp' not in telemetry:
                telemetry['timestamp'] = datetime.now().isoformat()
            
            self.telemetry_history.append(telemetry)
            
            # Keep only recent data points
            if len(self.telemetry_history) > self.analysis_window * 2:
                self.telemetry_history = self.telemetry_history[-self.analysis_window:]
            
            # Perform real-time analysis
            self._analyze_current_state(telemetry)
            
        except Exception as e:
            logger.error(f"Error adding telemetry data: {e}")
    
    def _analyze_current_state(self, current_telemetry: Dict[str, Any]) -> None:
        """Analyze current system state and generate alerts if needed."""
        try:
            alerts_generated = []
            
            # Memory usage analysis
            memory_alerts = self._analyze_memory_usage(current_telemetry)
            alerts_generated.extend(memory_alerts)
            
            # Task performance analysis
            performance_alerts = self._analyze_task_performance(current_telemetry)
            alerts_generated.extend(performance_alerts)
            
            # Agent health analysis
            agent_alerts = self._analyze_agent_health(current_telemetry)
            alerts_generated.extend(agent_alerts)
            
            # System stability analysis
            stability_alerts = self._analyze_system_stability(current_telemetry)
            alerts_generated.extend(stability_alerts)
            
            # Process new alerts
            for alert in alerts_generated:
                self._process_alert(alert)
                
        except Exception as e:
            logger.error(f"Error in current state analysis: {e}")
    
    def _analyze_memory_usage(self, telemetry: Dict[str, Any]) -> List[TelemetryAlert]:
        """Analyze memory usage patterns and generate alerts."""
        alerts = []
        
        try:
            if 'system_memory' in telemetry:
                memory_percent = telemetry['system_memory'].get('percent', 0)
                available_gb = telemetry['system_memory'].get('available_gb', 0)
                
                # Critical memory usage
                if memory_percent >= self.thresholds['memory_usage_critical']:
                    alert = TelemetryAlert(
                        id=f"memory_critical_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        severity=AlertSeverity.CRITICAL,
                        title="Critical Memory Usage",
                        description=f"Memory usage at {memory_percent:.1f}% (>{self.thresholds['memory_usage_critical']}%)",
                        timestamp=datetime.now(),
                        metrics={'memory_percent': memory_percent, 'available_gb': available_gb},
                        recommendations=[
                            "Enable aggressive consolidation mode",
                            "Scale down non-essential agents",
                            "Clear model caches",
                            "Consider adding more memory to the system"
                        ]
                    )
                    alerts.append(alert)
                
                # Warning memory usage
                elif memory_percent >= self.thresholds['memory_usage_warning']:
                    alert = TelemetryAlert(
                        id=f"memory_warning_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        severity=AlertSeverity.WARNING,
                        title="High Memory Usage",
                        description=f"Memory usage at {memory_percent:.1f}% (>{self.thresholds['memory_usage_warning']}%)",
                        timestamp=datetime.now(),
                        metrics={'memory_percent': memory_percent, 'available_gb': available_gb},
                        recommendations=[
                            "Consider enabling consolidation mode",
                            "Monitor for memory leaks",
                            "Optimize batch sizes"
                        ]
                    )
                    alerts.append(alert)
                
                # Low available memory
                if available_gb < 1.0:
                    alert = TelemetryAlert(
                        id=f"memory_low_available_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        severity=AlertSeverity.CRITICAL,
                        title="Extremely Low Available Memory",
                        description=f"Only {available_gb:.2f}GB available memory remaining",
                        timestamp=datetime.now(),
                        metrics={'available_gb': available_gb},
                        recommendations=[
                            "Immediately enable minimal processing mode",
                            "Stop non-essential processes",
                            "Restart system to clear memory leaks"
                        ]
                    )
                    alerts.append(alert)
        
        except Exception as e:
            logger.error(f"Error in memory analysis: {e}")
        
        return alerts
    
    def _analyze_task_performance(self, telemetry: Dict[str, Any]) -> List[TelemetryAlert]:
        """Analyze task performance metrics."""
        alerts = []
        
        try:
            # Analyze task duration trends
            if len(self.telemetry_history) >= 10:
                recent_durations = []
                for entry in self.telemetry_history[-10:]:
                    if 'task_durations' in entry:
                        recent_durations.extend(entry['task_durations'])
                
                if recent_durations:
                    avg_duration = statistics.mean(recent_durations)
                    
                    if avg_duration >= self.thresholds['avg_task_duration_critical']:
                        alert = TelemetryAlert(
                            id=f"task_duration_critical_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            severity=AlertSeverity.CRITICAL,
                            title="Critical Task Duration",
                            description=f"Average task duration {avg_duration:.1f}s (>{self.thresholds['avg_task_duration_critical']}s)",
                            timestamp=datetime.now(),
                            metrics={'avg_duration': avg_duration},
                            recommendations=[
                                "Enable task timeout mechanisms",
                                "Check for resource bottlenecks",
                                "Consider scaling up resources",
                                "Review task complexity"
                            ]
                        )
                        alerts.append(alert)
            
            # Analyze task failure rates
            task_failures = telemetry.get('task_failures', 0)
            total_tasks = telemetry.get('total_tasks', 1)
            failure_rate = (task_failures / total_tasks) * 100 if total_tasks > 0 else 0
            
            if failure_rate >= self.thresholds['task_failure_rate_critical']:
                alert = TelemetryAlert(
                    id=f"task_failure_critical_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    severity=AlertSeverity.CRITICAL,
                    title="High Task Failure Rate",
                    description=f"Task failure rate at {failure_rate:.1f}% (>{self.thresholds['task_failure_rate_critical']}%)",
                    timestamp=datetime.now(),
                    metrics={'failure_rate': failure_rate, 'failed_tasks': task_failures},
                    recommendations=[
                        "Review error logs for common failures",
                        "Check system resource availability",
                        "Implement task retry mechanisms",
                        "Consider reducing task complexity"
                    ]
                )
                alerts.append(alert)
        
        except Exception as e:
            logger.error(f"Error in task performance analysis: {e}")
        
        return alerts
    
    def _analyze_agent_health(self, telemetry: Dict[str, Any]) -> List[TelemetryAlert]:
        """Analyze agent health and spawning patterns."""
        alerts = []
        
        try:
            agent_status = telemetry.get('agent_status', {})
            active_tasks = agent_status.get('active_tasks', 0)
            consolidation_active = agent_status.get('consolidation_active', False)
            
            # Check for agent spawn failures
            if 'agent_spawn_failures' in telemetry:
                spawn_failures = telemetry['agent_spawn_failures']
                total_spawns = telemetry.get('total_spawn_attempts', 1)
                failure_rate = (spawn_failures / total_spawns) * 100 if total_spawns > 0 else 0
                
                if failure_rate >= self.thresholds['agent_spawn_failure_rate']:
                    alert = TelemetryAlert(
                        id=f"agent_spawn_failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        severity=AlertSeverity.WARNING,
                        title="High Agent Spawn Failure Rate",
                        description=f"Agent spawn failure rate at {failure_rate:.1f}%",
                        timestamp=datetime.now(),
                        metrics={'spawn_failure_rate': failure_rate},
                        recommendations=[
                            "Check memory availability",
                            "Review agent resource requirements",
                            "Consider adjusting spawn thresholds"
                        ]
                    )
                    alerts.append(alert)
            
            # Check for consolidation frequency
            if consolidation_active:
                recent_consolidations = sum(1 for entry in self.telemetry_history[-60:] 
                                          if entry.get('agent_status', {}).get('consolidation_active'))
                
                if recent_consolidations >= self.thresholds['consolidation_frequency_high']:
                    alert = TelemetryAlert(
                        id=f"frequent_consolidation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        severity=AlertSeverity.WARNING,
                        title="Frequent Agent Consolidations",
                        description=f"System consolidating frequently ({recent_consolidations} times in last hour)",
                        timestamp=datetime.now(),
                        metrics={'consolidation_count': recent_consolidations},
                        recommendations=[
                            "Consider increasing memory allocation",
                            "Review memory usage patterns",
                            "Check for memory leaks"
                        ]
                    )
                    alerts.append(alert)
        
        except Exception as e:
            logger.error(f"Error in agent health analysis: {e}")
        
        return alerts
    
    def _analyze_system_stability(self, telemetry: Dict[str, Any]) -> List[TelemetryAlert]:
        """Analyze overall system stability."""
        alerts = []
        
        try:
            # Check for rapid threshold changes
            if len(self.telemetry_history) >= 5:
                recent_thresholds = [
                    entry.get('memory_stats', {}).get('threshold_level', 'UNKNOWN')
                    for entry in self.telemetry_history[-5:]
                ]
                
                unique_thresholds = set(recent_thresholds)
                if len(unique_thresholds) >= 3:  # Rapid changes
                    alert = TelemetryAlert(
                        id=f"threshold_instability_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        severity=AlertSeverity.WARNING,
                        title="System Threshold Instability",
                        description="Memory thresholds changing rapidly, indicating system instability",
                        timestamp=datetime.now(),
                        metrics={'threshold_changes': list(recent_thresholds)},
                        recommendations=[
                            "Check for memory leaks",
                            "Review system load patterns",
                            "Consider increasing memory buffer",
                            "Monitor for external memory pressure"
                        ]
                    )
                    alerts.append(alert)
        
        except Exception as e:
            logger.error(f"Error in system stability analysis: {e}")
        
        return alerts
    
    def _process_alert(self, alert: TelemetryAlert) -> None:
        """Process and store an alert."""
        try:
            # Check if similar alert already exists
            similar_alert_exists = False
            for existing_id, existing_alert in self.active_alerts.items():
                if (existing_alert.title == alert.title and 
                    existing_alert.severity == alert.severity):
                    similar_alert_exists = True
                    break
            
            if not similar_alert_exists:
                self.active_alerts[alert.id] = alert
                self.alert_history.append(alert)
                
                # Log the alert
                logger.warning(f"ALERT [{alert.severity.value.upper()}]: {alert.title} - {alert.description}")
                
                # Keep only recent alerts in history
                if len(self.alert_history) > 1000:
                    self.alert_history = self.alert_history[-500:]
        
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
    
    def perform_trend_analysis(self, metric_name: str, days_back: int = 7) -> TrendAnalysis:
        """Perform detailed trend analysis for a specific metric."""
        try:
            # Get historical data for the metric
            historical_values = []
            timestamps = []
            
            cutoff_time = datetime.now() - timedelta(days=days_back)
            
            for entry in self.telemetry_history:
                entry_time = datetime.fromisoformat(entry.get('timestamp', ''))
                if entry_time >= cutoff_time:
                    value = self._extract_metric_value(entry, metric_name)
                    if value is not None:
                        historical_values.append(value)
                        timestamps.append(entry_time)
            
            if len(historical_values) < 5:
                return TrendAnalysis(
                    metric_name=metric_name,
                    direction=TrendDirection.STABLE,
                    slope=0.0,
                    confidence=0.0,
                    forecast_24h=None,
                    anomalies_detected=0,
                    recommendations=["Insufficient data for trend analysis"]
                )
            
            # Calculate trend
            slope = self._calculate_trend_slope(historical_values)
            direction = self._determine_trend_direction(slope, historical_values)
            confidence = self._calculate_trend_confidence(historical_values)
            forecast_24h = self._forecast_24h(historical_values, slope)
            anomalies = self._detect_anomalies(historical_values)
            recommendations = self._generate_trend_recommendations(metric_name, direction, slope, anomalies)
            
            return TrendAnalysis(
                metric_name=metric_name,
                direction=direction,
                slope=slope,
                confidence=confidence,
                forecast_24h=forecast_24h,
                anomalies_detected=len(anomalies),
                recommendations=recommendations
            )
        
        except Exception as e:
            logger.error(f"Error in trend analysis for {metric_name}: {e}")
            return TrendAnalysis(
                metric_name=metric_name,
                direction=TrendDirection.STABLE,
                slope=0.0,
                confidence=0.0,
                forecast_24h=None,
                anomalies_detected=0,
                recommendations=[f"Error in analysis: {e}"]
            )
    
    def _extract_metric_value(self, telemetry: Dict[str, Any], metric_name: str) -> Optional[float]:
        """Extract a specific metric value from telemetry data."""
        try:
            if metric_name == "memory_usage_percent":
                return telemetry.get('system_memory', {}).get('percent')
            elif metric_name == "available_memory_gb":
                return telemetry.get('system_memory', {}).get('available_gb')
            elif metric_name == "active_tasks":
                return telemetry.get('agent_status', {}).get('active_tasks')
            elif metric_name == "cpu_percent":
                return telemetry.get('cpu_stats', {}).get('cpu_percent')
            # Add more metric extractions as needed
            return None
        except:
            return None
    
    def _calculate_trend_slope(self, values: List[float]) -> float:
        """Calculate trend slope using linear regression."""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        
        # Simple linear regression
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _determine_trend_direction(self, slope: float, values: List[float]) -> TrendDirection:
        """Determine trend direction based on slope and volatility."""
        if len(values) < 2:
            return TrendDirection.STABLE
        
        # Calculate volatility
        volatility = statistics.stdev(values) / statistics.mean(values) if statistics.mean(values) != 0 else 0
        
        if volatility > 0.3:  # High volatility
            return TrendDirection.VOLATILE
        elif abs(slope) < 0.01:  # Minimal slope
            return TrendDirection.STABLE
        elif slope > 0:
            return TrendDirection.INCREASING
        else:
            return TrendDirection.DECREASING
    
    def _calculate_trend_confidence(self, values: List[float]) -> float:
        """Calculate confidence in trend analysis."""
        if len(values) < 5:
            return 0.0
        
        # Simple confidence based on data consistency
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        
        # Lower standard deviation relative to mean = higher confidence
        if mean_val == 0:
            return 0.0
        
        coefficient_of_variation = std_val / abs(mean_val)
        confidence = max(0.0, min(1.0, 1.0 - coefficient_of_variation))
        
        return confidence
    
    def _forecast_24h(self, values: List[float], slope: float) -> Optional[float]:
        """Simple 24-hour forecast based on trend."""
        if len(values) == 0:
            return None
        
        # Assuming data points are roughly hourly, predict 24 hours ahead
        current_value = values[-1]
        forecast = current_value + (slope * 24)
        
        return max(0, forecast)  # Ensure non-negative
    
    def _detect_anomalies(self, values: List[float]) -> List[int]:
        """Detect anomalies in the data using simple statistical methods."""
        if len(values) < 5:
            return []
        
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        threshold = 2 * std_val  # 2 standard deviations
        
        anomalies = []
        for i, value in enumerate(values):
            if abs(value - mean_val) > threshold:
                anomalies.append(i)
        
        return anomalies
    
    def _generate_trend_recommendations(
        self, 
        metric_name: str, 
        direction: TrendDirection, 
        slope: float, 
        anomalies: List[int]
    ) -> List[str]:
        """Generate recommendations based on trend analysis."""
        recommendations = []
        
        if metric_name == "memory_usage_percent":
            if direction == TrendDirection.INCREASING:
                recommendations.extend([
                    "Memory usage is trending upward",
                    "Consider enabling proactive consolidation",
                    "Monitor for memory leaks",
                    "Plan for memory scaling"
                ])
            elif direction == TrendDirection.VOLATILE:
                recommendations.extend([
                    "Memory usage is highly volatile",
                    "Check for irregular workload patterns",
                    "Consider smoothing memory allocation"
                ])
        
        elif metric_name == "active_tasks":
            if direction == TrendDirection.INCREASING:
                recommendations.extend([
                    "Task load is increasing",
                    "Consider scaling out workers",
                    "Monitor queue depths"
                ])
        
        if len(anomalies) > 2:
            recommendations.append(f"Detected {len(anomalies)} anomalies - investigate irregular patterns")
        
        return recommendations
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[TelemetryAlert]:
        """Get currently active alerts, optionally filtered by severity."""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Manually resolve an alert."""
        if alert_id in self.active_alerts:
            del self.active_alerts[alert_id]
            logger.info(f"Alert {alert_id} resolved manually")
            return True
        return False
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get a comprehensive system health summary."""
        try:
            active_critical = len([a for a in self.active_alerts.values() if a.severity == AlertSeverity.CRITICAL])
            active_warning = len([a for a in self.active_alerts.values() if a.severity == AlertSeverity.WARNING])
            
            # Get latest telemetry
            latest = self.telemetry_history[-1] if self.telemetry_history else {}
            
            # Calculate overall health score (0-100)
            health_score = 100
            health_score -= active_critical * 20  # Critical alerts significantly impact score
            health_score -= active_warning * 5   # Warning alerts have moderate impact
            health_score = max(0, health_score)
            
            # Determine health status
            if health_score >= 90:
                status = "excellent"
            elif health_score >= 75:
                status = "good"
            elif health_score >= 50:
                status = "fair"
            elif health_score >= 25:
                status = "poor"
            else:
                status = "critical"
            
            return {
                "overall_health_score": health_score,
                "health_status": status,
                "active_alerts": {
                    "critical": active_critical,
                    "warning": active_warning,
                    "total": len(self.active_alerts)
                },
                "latest_metrics": latest,
                "data_points_analyzed": len(self.telemetry_history),
                "analysis_timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error generating health summary: {e}")
            return {
                "overall_health_score": 0,
                "health_status": "unknown",
                "error": str(e)
            }


# Global telemetry analyzer instance
telemetry_analyzer = TelemetryAnalyzer()
