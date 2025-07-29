"""
Health monitoring routes for Ray's system health status
"""

from fastapi import APIRouter
from typing import Optional
import logging
from datetime import datetime

from modules.health.handler import HealthHandler
from modules.health.models import HealthCheckRequest
from utils.timestamp_utils import add_ray_timestamp_to_response, get_ray_time_context

logger = logging.getLogger(__name__)

# Create router
health_router = APIRouter(prefix="/health", tags=["health"])

# Initialize handler
health_handler = HealthHandler()


@health_router.get("/status")
async def get_health_status(
    detailed: Optional[bool] = True,
    trends: Optional[bool] = True,
    recommendations: Optional[bool] = True,
    external_checks: Optional[bool] = True
):
    """
    Get Ray's comprehensive health status
    
    No parameters required - Ray just calls this to get her complete health report
    """
    try:
        # Create health check request
        request = HealthCheckRequest(
            include_detailed_metrics=detailed,
            include_trends=trends,
            include_recommendations=recommendations,
            check_external_services=external_checks
        )
        
        # Get health status
        health_status = health_handler.get_health_status(request)
        
        # Convert to dict for JSON response
        result = {
            # Overall status
            "overall_status": health_status.overall_status.value,
            "status_message": health_status.status_message,
            "timestamp": health_status.timestamp.isoformat(),
            "uptime_seconds": health_status.uptime_seconds,
            "uptime_human": _format_uptime(health_status.uptime_seconds),
            
            # System vitals
            "system_metrics": {
                "cpu_usage_percent": health_status.system_metrics.cpu_usage_percent,
                "memory_usage_percent": health_status.system_metrics.memory_usage_percent,
                "memory_used_mb": health_status.system_metrics.memory_used_mb,
                "memory_total_mb": health_status.system_metrics.memory_total_mb,
                "disk_usage_percent": health_status.system_metrics.disk_usage_percent,
                "disk_used_gb": health_status.system_metrics.disk_used_gb,
                "disk_total_gb": health_status.system_metrics.disk_total_gb,
                "load_average": health_status.system_metrics.load_average,
                "process_count": health_status.system_metrics.process_count,
                "thread_count": health_status.system_metrics.thread_count,
                "network_io": health_status.system_metrics.network_io
            },
            
            # Service health
            "services": [
                {
                    "name": service.name,
                    "state": service.state.value,
                    "uptime_seconds": service.uptime_seconds,
                    "memory_usage_mb": service.memory_usage_mb,
                    "cpu_usage_percent": service.cpu_usage_percent,
                    "last_heartbeat": service.last_heartbeat.isoformat() if service.last_heartbeat else None,
                    "error_count": service.error_count,
                    "response_time_ms": service.response_time_ms,
                    "health_check_passed": service.health_check_passed,
                    "details": service.details
                } for service in health_status.services
            ],
            
            # Network health
            "network_health": {
                "internet_connected": health_status.network_health.internet_connected,
                "dns_resolution_ms": health_status.network_health.dns_resolution_ms,
                "external_api_status": health_status.network_health.external_api_status,
                "latency_ms": health_status.network_health.latency_ms,
                "packet_loss_percent": health_status.network_health.packet_loss_percent
            },
            
            # Security health
            "security_health": {
                "firewall_active": health_status.security_health.firewall_active,
                "threat_level": health_status.security_health.threat_level,
                "failed_login_attempts": health_status.security_health.failed_login_attempts,
                "suspicious_activity_count": health_status.security_health.suspicious_activity_count,
                "encryption_status": health_status.security_health.encryption_status,
                "last_security_scan": health_status.security_health.last_security_scan.isoformat() if health_status.security_health.last_security_scan else None
            },
            
            # Application health
            "application_health": {
                "modules_loaded": health_status.application_health.modules_loaded,
                "modules_failed": health_status.application_health.modules_failed,
                "active_sessions": health_status.application_health.active_sessions,
                "task_queue_size": health_status.application_health.task_queue_size,
                "memory_leaks_detected": health_status.application_health.memory_leaks_detected,
                "error_rate_per_hour": health_status.application_health.error_rate_per_hour,
                "average_response_time_ms": health_status.application_health.average_response_time_ms,
                "cache_hit_rate_percent": health_status.application_health.cache_hit_rate_percent
            },
            
            # Database health (if available)
            "database_health": {
                "connected": health_status.database_health.connected,
                "response_time_ms": health_status.database_health.response_time_ms,
                "active_connections": health_status.database_health.active_connections,
                "max_connections": health_status.database_health.max_connections,
                "error_rate": health_status.database_health.error_rate,
                "storage_used_mb": health_status.database_health.storage_used_mb
            } if health_status.database_health else None,
            
            # Active alerts
            "active_alerts": [
                {
                    "level": alert.level,
                    "category": alert.category,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "resolved": alert.resolved,
                    "suggested_action": alert.suggested_action
                } for alert in health_status.active_alerts
            ],
            
            # Health trends
            "health_trends": [
                {
                    "metric_name": trend.metric_name,
                    "current_value": trend.current_value,
                    "trend_direction": trend.trend_direction,
                    "change_percent": trend.change_percent,
                    "time_period": trend.time_period,
                    "prediction": trend.prediction
                } for trend in health_status.health_trends
            ] if trends else [],
            
            # Performance metrics
            "performance_score": health_status.performance_score,
            "availability_percent": health_status.availability_percent,
            
            # Recommendations
            "recommendations": health_status.recommendations if recommendations else [],
            
            # Ray-specific metrics
            "consciousness_metrics": health_status.consciousness_metrics,
            "learning_metrics": health_status.learning_metrics,
            "memory_system_health": health_status.memory_system_health,
            
            # Historical context
            "health_history_summary": health_status.health_history_summary,
            "last_health_check": health_status.last_health_check.isoformat(),
            "next_scheduled_check": health_status.next_scheduled_check.isoformat()
        }
        
        logger.info(f"Health status retrieved - Overall: {health_status.overall_status.value}")
        
        # Add comprehensive timestamp information for Ray
        result = add_ray_timestamp_to_response(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving health status: {str(e)}")
        return {
            "overall_status": "error",
            "status_message": f"Health check failed: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "error": True
        }


@health_router.get("/quick")
async def get_quick_health():
    """
    Get a quick health summary for Ray
    """
    try:
        request = HealthCheckRequest(
            include_detailed_metrics=False,
            include_trends=False,
            include_recommendations=False,
            check_external_services=False
        )
        
        health_status = health_handler.get_health_status(request)
        
        return {
            "overall_status": health_status.overall_status.value,
            "status_message": health_status.status_message,
            "performance_score": health_status.performance_score,
            "cpu_usage": health_status.system_metrics.cpu_usage_percent,
            "memory_usage": health_status.system_metrics.memory_usage_percent,
            "disk_usage": health_status.system_metrics.disk_usage_percent,
            "services_running": len([s for s in health_status.services if s.state.value == "running"]),
            "services_total": len(health_status.services),
            "active_alerts": len(health_status.active_alerts),
            "timestamp": health_status.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving quick health status: {str(e)}")
        return {
            "overall_status": "error",
            "status_message": f"Quick health check failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@health_router.get("/vitals")
async def get_system_vitals():
    """
    Get just the core system vitals for Ray
    """
    try:
        health_status = health_handler.get_health_status()
        
        return {
            "cpu_usage_percent": health_status.system_metrics.cpu_usage_percent,
            "memory_usage_percent": health_status.system_metrics.memory_usage_percent,
            "disk_usage_percent": health_status.system_metrics.disk_usage_percent,
            "uptime_seconds": health_status.uptime_seconds,
            "uptime_human": _format_uptime(health_status.uptime_seconds),
            "performance_score": health_status.performance_score,
            "consciousness_coherence": health_status.consciousness_metrics.get("consciousness_coherence", 0),
            "learning_velocity": health_status.learning_metrics.get("learning_rate", 0),
            "memory_health": health_status.memory_system_health.get("memory_coherence", 0),
            "timestamp": health_status.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving system vitals: {str(e)}")
        return {
            "error": f"Vitals check failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


def _format_uptime(uptime_seconds: float) -> str:
    """Format uptime in human-readable format"""
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"