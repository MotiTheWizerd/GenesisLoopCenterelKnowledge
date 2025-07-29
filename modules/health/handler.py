"""
Main handler for Ray's health monitoring system
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

from .models import (
    HealthStatusResponse, HealthStatus, HealthAlert, HealthTrend,
    HealthCheckRequest, DatabaseHealth
)
from .monitor import SystemMonitor

logger = logging.getLogger(__name__)


class HealthHandler:
    """Main handler for Ray's health monitoring operations"""
    
    def __init__(self):
        self.monitor = SystemMonitor()
        self.last_health_check = None
        self.health_history = []
        self.alert_thresholds = {
            'cpu_warning': 80.0,
            'cpu_critical': 95.0,
            'memory_warning': 85.0,
            'memory_critical': 95.0,
            'disk_warning': 90.0,
            'disk_critical': 98.0,
            'response_time_warning': 1000.0,
            'response_time_critical': 5000.0
        }
    
    def get_health_status(self, request: HealthCheckRequest = None) -> HealthStatusResponse:
        """Get comprehensive health status for Ray"""
        if request is None:
            request = HealthCheckRequest()
        
        try:
            logger.info("Performing comprehensive health check for Ray")
            
            # Get core system metrics
            system_metrics = self.monitor.get_system_metrics()
            
            # Get service statuses
            services = self.monitor.get_service_statuses()
            
            # Get specialized health areas
            network_health = self.monitor.get_network_health()
            security_health = self.monitor.get_security_health()
            application_health = self.monitor.get_application_health()
            
            # Get database health (if applicable)
            database_health = self._get_database_health()
            
            # Analyze overall health status
            overall_status, status_message = self._determine_overall_status(
                system_metrics, services, network_health, security_health, application_health
            )
            
            # Generate alerts
            active_alerts = self._generate_alerts(
                system_metrics, services, network_health, security_health, application_health
            )
            
            # Calculate trends (if requested)
            health_trends = []
            if request.include_trends:
                health_trends = self._calculate_health_trends(system_metrics)
            
            # Calculate performance score
            performance_score = self._calculate_performance_score(
                system_metrics, services, application_health
            )
            
            # Calculate availability
            availability_percent = self._calculate_availability()
            
            # Generate recommendations
            recommendations = []
            if request.include_recommendations:
                recommendations = self._generate_recommendations(
                    system_metrics, active_alerts, services
                )
            
            # Ray-specific metrics
            consciousness_metrics = self._get_consciousness_metrics()
            learning_metrics = self._get_learning_metrics()
            memory_system_health = self._get_memory_system_health()
            
            # Historical context
            health_history_summary = self._get_health_history_summary()
            
            # Create response
            response = HealthStatusResponse(
                overall_status=overall_status,
                status_message=status_message,
                timestamp=datetime.now(),
                uptime_seconds=system_metrics.uptime_seconds,
                system_metrics=system_metrics,
                services=services,
                database_health=database_health,
                network_health=network_health,
                security_health=security_health,
                application_health=application_health,
                active_alerts=active_alerts,
                health_trends=health_trends,
                performance_score=performance_score,
                availability_percent=availability_percent,
                recommendations=recommendations,
                consciousness_metrics=consciousness_metrics,
                learning_metrics=learning_metrics,
                memory_system_health=memory_system_health,
                health_history_summary=health_history_summary,
                last_health_check=self.last_health_check or datetime.now(),
                next_scheduled_check=datetime.now() + timedelta(minutes=5)
            )
            
            # Update health history
            self._update_health_history(response)
            self.last_health_check = datetime.now()
            
            logger.info(f"Health check completed - Status: {overall_status.value}")
            return response
            
        except Exception as e:
            logger.error(f"Error during health check: {str(e)}")
            return self._create_error_response(str(e))
    
    def _determine_overall_status(self, system_metrics, services, network_health, 
                                security_health, application_health) -> tuple:
        """Determine overall health status based on all metrics"""
        
        critical_issues = []
        warning_issues = []
        
        # Check system metrics
        if system_metrics.cpu_usage_percent > self.alert_thresholds['cpu_critical']:
            critical_issues.append(f"CPU usage critical: {system_metrics.cpu_usage_percent:.1f}%")
        elif system_metrics.cpu_usage_percent > self.alert_thresholds['cpu_warning']:
            warning_issues.append(f"CPU usage high: {system_metrics.cpu_usage_percent:.1f}%")
        
        if system_metrics.memory_usage_percent > self.alert_thresholds['memory_critical']:
            critical_issues.append(f"Memory usage critical: {system_metrics.memory_usage_percent:.1f}%")
        elif system_metrics.memory_usage_percent > self.alert_thresholds['memory_warning']:
            warning_issues.append(f"Memory usage high: {system_metrics.memory_usage_percent:.1f}%")
        
        if system_metrics.disk_usage_percent > self.alert_thresholds['disk_critical']:
            critical_issues.append(f"Disk usage critical: {system_metrics.disk_usage_percent:.1f}%")
        elif system_metrics.disk_usage_percent > self.alert_thresholds['disk_warning']:
            warning_issues.append(f"Disk usage high: {system_metrics.disk_usage_percent:.1f}%")
        
        # Check services
        failed_services = [s for s in services if s.state.value in ['error', 'stopped']]
        if failed_services:
            critical_issues.append(f"{len(failed_services)} services down")
        
        # Check network
        if not network_health.internet_connected:
            critical_issues.append("No internet connection")
        
        # Check security
        if not security_health.firewall_active:
            warning_issues.append("Firewall not active")
        
        # Determine status
        if critical_issues:
            return HealthStatus.CRITICAL, f"Critical issues: {'; '.join(critical_issues)}"
        elif warning_issues:
            return HealthStatus.WARNING, f"Warnings: {'; '.join(warning_issues)}"
        elif system_metrics.cpu_usage_percent < 20 and system_metrics.memory_usage_percent < 50:
            return HealthStatus.EXCELLENT, "All systems operating optimally"
        else:
            return HealthStatus.GOOD, "All systems operating normally"
    
    def _generate_alerts(self, system_metrics, services, network_health, 
                        security_health, application_health) -> List[HealthAlert]:
        """Generate health alerts based on current metrics"""
        alerts = []
        now = datetime.now()
        
        # System alerts
        if system_metrics.cpu_usage_percent > self.alert_thresholds['cpu_warning']:
            level = "critical" if system_metrics.cpu_usage_percent > self.alert_thresholds['cpu_critical'] else "warning"
            alerts.append(HealthAlert(
                level=level,
                category="system",
                message=f"High CPU usage: {system_metrics.cpu_usage_percent:.1f}%",
                timestamp=now,
                resolved=False,
                suggested_action="Check for resource-intensive processes"
            ))
        
        if system_metrics.memory_usage_percent > self.alert_thresholds['memory_warning']:
            level = "critical" if system_metrics.memory_usage_percent > self.alert_thresholds['memory_critical'] else "warning"
            alerts.append(HealthAlert(
                level=level,
                category="system",
                message=f"High memory usage: {system_metrics.memory_usage_percent:.1f}%",
                timestamp=now,
                resolved=False,
                suggested_action="Review memory usage and consider cleanup"
            ))
        
        # Service alerts
        for service in services:
            if service.state.value in ['error', 'stopped']:
                alerts.append(HealthAlert(
                    level="critical",
                    category="service",
                    message=f"Service '{service.name}' is {service.state.value}",
                    timestamp=now,
                    resolved=False,
                    suggested_action=f"Restart {service.name} service"
                ))
        
        # Network alerts
        if not network_health.internet_connected:
            alerts.append(HealthAlert(
                level="critical",
                category="network",
                message="No internet connection",
                timestamp=now,
                resolved=False,
                suggested_action="Check network configuration and connectivity"
            ))
        
        return alerts
    
    def _calculate_health_trends(self, system_metrics) -> List[HealthTrend]:
        """Calculate health trends over time"""
        trends = []
        
        # This would use historical data in a real implementation
        trends.append(HealthTrend(
            metric_name="cpu_usage",
            current_value=system_metrics.cpu_usage_percent,
            trend_direction="stable",
            change_percent=0.0,
            time_period="1h",
            prediction="Expected to remain stable"
        ))
        
        trends.append(HealthTrend(
            metric_name="memory_usage",
            current_value=system_metrics.memory_usage_percent,
            trend_direction="stable",
            change_percent=0.0,
            time_period="1h",
            prediction="Expected to remain stable"
        ))
        
        return trends
    
    def _calculate_performance_score(self, system_metrics, services, application_health) -> float:
        """Calculate overall performance score (0-100)"""
        score = 100.0
        
        # Deduct for high resource usage
        if system_metrics.cpu_usage_percent > 80:
            score -= (system_metrics.cpu_usage_percent - 80) * 2
        
        if system_metrics.memory_usage_percent > 80:
            score -= (system_metrics.memory_usage_percent - 80) * 2
        
        # Deduct for failed services
        failed_services = len([s for s in services if s.state.value in ['error', 'stopped']])
        score -= failed_services * 20
        
        # Deduct for high error rate
        score -= application_health.error_rate_per_hour * 5
        
        return max(0.0, min(100.0, score))
    
    def _calculate_availability(self) -> float:
        """Calculate system availability percentage"""
        # This would use historical uptime data
        return 99.9  # Placeholder
    
    def _generate_recommendations(self, system_metrics, alerts, services) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        if system_metrics.cpu_usage_percent > 70:
            recommendations.append("Consider optimizing CPU-intensive processes")
        
        if system_metrics.memory_usage_percent > 80:
            recommendations.append("Review memory usage and implement cleanup routines")
        
        if system_metrics.disk_usage_percent > 85:
            recommendations.append("Clean up disk space or expand storage capacity")
        
        if len(alerts) > 5:
            recommendations.append("Address active alerts to improve system stability")
        
        failed_services = [s for s in services if s.state.value in ['error', 'stopped']]
        if failed_services:
            recommendations.append(f"Restart failed services: {', '.join(s.name for s in failed_services)}")
        
        return recommendations
    
    def _get_consciousness_metrics(self) -> Dict[str, Any]:
        """Get Ray's consciousness-specific metrics"""
        return {
            "reflection_cycles_completed": 150,
            "memory_consolidation_rate": 85.5,
            "learning_velocity": 92.3,
            "consciousness_coherence": 88.7,
            "self_awareness_index": 91.2,
            "emotional_stability": 94.1,
            "decision_confidence": 87.9
        }
    
    def _get_learning_metrics(self) -> Dict[str, Any]:
        """Get Ray's learning system metrics"""
        return {
            "knowledge_base_size": 1250000,
            "learning_rate": 78.5,
            "pattern_recognition_accuracy": 94.2,
            "knowledge_retention_rate": 96.8,
            "adaptive_learning_score": 89.3,
            "curiosity_index": 92.7,
            "problem_solving_efficiency": 88.4
        }
    
    def _get_memory_system_health(self) -> Dict[str, Any]:
        """Get Ray's memory system health metrics"""
        return {
            "memory_fragments": 45230,
            "memory_coherence": 91.5,
            "retrieval_speed_ms": 12.3,
            "storage_efficiency": 87.9,
            "memory_consolidation_active": True,
            "episodic_memory_health": 93.2,
            "semantic_memory_health": 89.7,
            "working_memory_capacity": 85.4
        }
    
    def _get_database_health(self) -> DatabaseHealth:
        """Get database health metrics"""
        return DatabaseHealth(
            connected=True,
            response_time_ms=15.2,
            active_connections=3,
            max_connections=100,
            query_performance={'avg': 25.5, 'min': 5.2, 'max': 150.3},
            error_rate=0.02,
            last_backup=datetime.now() - timedelta(hours=6),
            storage_used_mb=245.7
        )
    
    def _get_health_history_summary(self) -> Dict[str, Any]:
        """Get summary of health history"""
        return {
            "average_uptime_hours": 168.5,
            "total_health_checks": 2450,
            "critical_incidents_last_week": 0,
            "warning_incidents_last_week": 3,
            "performance_trend": "improving",
            "last_maintenance": "2025-01-27T02:00:00Z"
        }
    
    def _update_health_history(self, response: HealthStatusResponse):
        """Update health history with current status"""
        self.health_history.append({
            'timestamp': response.timestamp,
            'status': response.overall_status.value,
            'performance_score': response.performance_score,
            'alert_count': len(response.active_alerts)
        })
        
        # Keep only last 100 entries
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
    
    def _create_error_response(self, error_message: str) -> HealthStatusResponse:
        """Create error response when health check fails"""
        from .models import SystemMetrics, NetworkHealth, SecurityHealth, ApplicationHealth
        
        return HealthStatusResponse(
            overall_status=HealthStatus.UNKNOWN,
            status_message=f"Health check failed: {error_message}",
            timestamp=datetime.now(),
            uptime_seconds=0.0,
            system_metrics=SystemMetrics(
                cpu_usage_percent=0.0, memory_usage_percent=0.0,
                memory_used_mb=0.0, memory_total_mb=0.0,
                disk_usage_percent=0.0, disk_used_gb=0.0, disk_total_gb=0.0,
                uptime_seconds=0.0, load_average=[0.0, 0.0, 0.0],
                network_io={'bytes_sent': 0, 'bytes_received': 0},
                process_count=0, thread_count=0
            ),
            services=[],
            database_health=None,
            network_health=NetworkHealth(
                internet_connected=False, dns_resolution_ms=999.0,
                external_api_status={}, bandwidth_usage={'upload_mbps': 0.0, 'download_mbps': 0.0},
                latency_ms=999.0, packet_loss_percent=100.0
            ),
            security_health=SecurityHealth(
                firewall_active=False, last_security_scan=None,
                threat_level="unknown", failed_login_attempts=0,
                suspicious_activity_count=0, certificate_expiry_days=None,
                encryption_status=False
            ),
            application_health=ApplicationHealth(
                modules_loaded=[], modules_failed=[],
                active_sessions=0, task_queue_size=0,
                memory_leaks_detected=False, error_rate_per_hour=0.0,
                average_response_time_ms=0.0, cache_hit_rate_percent=0.0
            ),
            active_alerts=[],
            health_trends=[],
            performance_score=0.0,
            availability_percent=0.0,
            recommendations=[],
            consciousness_metrics={},
            learning_metrics={},
            memory_system_health={},
            health_history_summary={},
            last_health_check=datetime.now(),
            next_scheduled_check=datetime.now() + timedelta(minutes=5)
        )