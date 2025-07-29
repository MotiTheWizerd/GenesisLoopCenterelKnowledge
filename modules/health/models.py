"""
Data models for Ray's health monitoring system
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class HealthStatus(Enum):
    """Overall health status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ServiceState(Enum):
    """Individual service states"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"


@dataclass
class SystemMetrics:
    """Core system performance metrics"""
    cpu_usage_percent: float
    memory_usage_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_usage_percent: float
    disk_used_gb: float
    disk_total_gb: float
    uptime_seconds: float
    load_average: List[float]  # 1min, 5min, 15min
    network_io: Dict[str, int]  # bytes_sent, bytes_received
    process_count: int
    thread_count: int


@dataclass
class ServiceStatus:
    """Individual service health status"""
    name: str
    state: ServiceState
    uptime_seconds: float
    memory_usage_mb: float
    cpu_usage_percent: float
    last_heartbeat: Optional[datetime]
    error_count: int
    response_time_ms: float
    health_check_passed: bool
    details: Dict[str, Any]


@dataclass
class DatabaseHealth:
    """Database connection and performance health"""
    connected: bool
    response_time_ms: float
    active_connections: int
    max_connections: int
    query_performance: Dict[str, float]  # avg, min, max query times
    error_rate: float
    last_backup: Optional[datetime]
    storage_used_mb: float


@dataclass
class NetworkHealth:
    """Network connectivity and performance"""
    internet_connected: bool
    dns_resolution_ms: float
    external_api_status: Dict[str, bool]  # service_name: is_reachable
    bandwidth_usage: Dict[str, float]  # upload_mbps, download_mbps
    latency_ms: float
    packet_loss_percent: float


@dataclass
class SecurityHealth:
    """Security status and threat monitoring"""
    firewall_active: bool
    last_security_scan: Optional[datetime]
    threat_level: str
    failed_login_attempts: int
    suspicious_activity_count: int
    certificate_expiry_days: Optional[int]
    encryption_status: bool


@dataclass
class ApplicationHealth:
    """Ray's application-specific health metrics"""
    modules_loaded: List[str]
    modules_failed: List[str]
    active_sessions: int
    task_queue_size: int
    memory_leaks_detected: bool
    error_rate_per_hour: float
    average_response_time_ms: float
    cache_hit_rate_percent: float


@dataclass
class HealthAlert:
    """Health alert/warning information"""
    level: str  # info, warning, critical
    category: str  # system, service, security, etc.
    message: str
    timestamp: datetime
    resolved: bool
    suggested_action: Optional[str]


@dataclass
class HealthTrend:
    """Health trend analysis"""
    metric_name: str
    current_value: float
    trend_direction: str  # improving, stable, degrading
    change_percent: float
    time_period: str
    prediction: Optional[str]


@dataclass
class HealthStatusResponse:
    """Complete health status response for Ray"""
    # Overall status
    overall_status: HealthStatus
    status_message: str
    timestamp: datetime
    uptime_seconds: float
    
    # Core metrics
    system_metrics: SystemMetrics
    
    # Service statuses
    services: List[ServiceStatus]
    
    # Specialized health areas
    database_health: Optional[DatabaseHealth]
    network_health: NetworkHealth
    security_health: SecurityHealth
    application_health: ApplicationHealth
    
    # Alerts and trends
    active_alerts: List[HealthAlert]
    health_trends: List[HealthTrend]
    
    # Performance summary
    performance_score: float  # 0-100
    availability_percent: float  # uptime percentage
    
    # Resource recommendations
    recommendations: List[str]
    
    # Ray-specific vitals
    consciousness_metrics: Dict[str, Any]
    learning_metrics: Dict[str, Any]
    memory_system_health: Dict[str, Any]
    
    # Historical context
    health_history_summary: Dict[str, Any]
    last_health_check: datetime
    next_scheduled_check: datetime


@dataclass
class HealthCheckRequest:
    """Request for health status (no parameters needed for general health)"""
    include_detailed_metrics: bool = True
    include_trends: bool = True
    include_recommendations: bool = True
    check_external_services: bool = True