"""
Tests for health module models
"""

import pytest
from datetime import datetime
from modules.health.models import (
    HealthStatus, ServiceState, SystemMetrics, ServiceStatus,
    HealthStatusResponse, HealthAlert, HealthTrend, NetworkHealth,
    SecurityHealth, ApplicationHealth, DatabaseHealth
)


class TestHealthStatus:
    def test_health_status_enum(self):
        assert HealthStatus.EXCELLENT.value == "excellent"
        assert HealthStatus.GOOD.value == "good"
        assert HealthStatus.WARNING.value == "warning"
        assert HealthStatus.CRITICAL.value == "critical"
        assert HealthStatus.UNKNOWN.value == "unknown"


class TestServiceState:
    def test_service_state_enum(self):
        assert ServiceState.RUNNING.value == "running"
        assert ServiceState.STOPPED.value == "stopped"
        assert ServiceState.ERROR.value == "error"
        assert ServiceState.STARTING.value == "starting"
        assert ServiceState.STOPPING.value == "stopping"


class TestSystemMetrics:
    def test_system_metrics_creation(self):
        metrics = SystemMetrics(
            cpu_usage_percent=45.5,
            memory_usage_percent=67.2,
            memory_used_mb=2048.0,
            memory_total_mb=4096.0,
            disk_usage_percent=78.9,
            disk_used_gb=150.5,
            disk_total_gb=500.0,
            uptime_seconds=86400.0,
            load_average=[1.2, 1.5, 1.8],
            network_io={'bytes_sent': 1000000, 'bytes_received': 2000000},
            process_count=150,
            thread_count=800
        )
        
        assert metrics.cpu_usage_percent == 45.5
        assert metrics.memory_usage_percent == 67.2
        assert metrics.memory_used_mb == 2048.0
        assert metrics.memory_total_mb == 4096.0
        assert metrics.disk_usage_percent == 78.9
        assert metrics.uptime_seconds == 86400.0
        assert len(metrics.load_average) == 3
        assert metrics.network_io['bytes_sent'] == 1000000
        assert metrics.process_count == 150
        assert metrics.thread_count == 800


class TestServiceStatus:
    def test_service_status_creation(self):
        now = datetime.now()
        service = ServiceStatus(
            name="test_service",
            state=ServiceState.RUNNING,
            uptime_seconds=3600.0,
            memory_usage_mb=128.5,
            cpu_usage_percent=15.2,
            last_heartbeat=now,
            error_count=0,
            response_time_ms=25.5,
            health_check_passed=True,
            details={'status': 'healthy', 'version': '1.0.0'}
        )
        
        assert service.name == "test_service"
        assert service.state == ServiceState.RUNNING
        assert service.uptime_seconds == 3600.0
        assert service.memory_usage_mb == 128.5
        assert service.cpu_usage_percent == 15.2
        assert service.last_heartbeat == now
        assert service.error_count == 0
        assert service.response_time_ms == 25.5
        assert service.health_check_passed == True
        assert service.details['status'] == 'healthy'


class TestNetworkHealth:
    def test_network_health_creation(self):
        network = NetworkHealth(
            internet_connected=True,
            dns_resolution_ms=15.5,
            external_api_status={'google': True, 'github': True},
            bandwidth_usage={'upload_mbps': 10.5, 'download_mbps': 50.2},
            latency_ms=25.8,
            packet_loss_percent=0.1
        )
        
        assert network.internet_connected == True
        assert network.dns_resolution_ms == 15.5
        assert network.external_api_status['google'] == True
        assert network.bandwidth_usage['upload_mbps'] == 10.5
        assert network.latency_ms == 25.8
        assert network.packet_loss_percent == 0.1


class TestSecurityHealth:
    def test_security_health_creation(self):
        now = datetime.now()
        security = SecurityHealth(
            firewall_active=True,
            last_security_scan=now,
            threat_level="low",
            failed_login_attempts=2,
            suspicious_activity_count=0,
            certificate_expiry_days=90,
            encryption_status=True
        )
        
        assert security.firewall_active == True
        assert security.last_security_scan == now
        assert security.threat_level == "low"
        assert security.failed_login_attempts == 2
        assert security.suspicious_activity_count == 0
        assert security.certificate_expiry_days == 90
        assert security.encryption_status == True


class TestApplicationHealth:
    def test_application_health_creation(self):
        app_health = ApplicationHealth(
            modules_loaded=['heartbeat', 'reflect', 'memory'],
            modules_failed=['broken_module'],
            active_sessions=5,
            task_queue_size=12,
            memory_leaks_detected=False,
            error_rate_per_hour=0.5,
            average_response_time_ms=45.2,
            cache_hit_rate_percent=85.7
        )
        
        assert len(app_health.modules_loaded) == 3
        assert 'heartbeat' in app_health.modules_loaded
        assert len(app_health.modules_failed) == 1
        assert 'broken_module' in app_health.modules_failed
        assert app_health.active_sessions == 5
        assert app_health.task_queue_size == 12
        assert app_health.memory_leaks_detected == False
        assert app_health.error_rate_per_hour == 0.5
        assert app_health.average_response_time_ms == 45.2
        assert app_health.cache_hit_rate_percent == 85.7


class TestHealthAlert:
    def test_health_alert_creation(self):
        now = datetime.now()
        alert = HealthAlert(
            level="warning",
            category="system",
            message="High CPU usage detected",
            timestamp=now,
            resolved=False,
            suggested_action="Check for resource-intensive processes"
        )
        
        assert alert.level == "warning"
        assert alert.category == "system"
        assert alert.message == "High CPU usage detected"
        assert alert.timestamp == now
        assert alert.resolved == False
        assert alert.suggested_action == "Check for resource-intensive processes"


class TestHealthTrend:
    def test_health_trend_creation(self):
        trend = HealthTrend(
            metric_name="cpu_usage",
            current_value=45.5,
            trend_direction="increasing",
            change_percent=5.2,
            time_period="1h",
            prediction="Expected to stabilize"
        )
        
        assert trend.metric_name == "cpu_usage"
        assert trend.current_value == 45.5
        assert trend.trend_direction == "increasing"
        assert trend.change_percent == 5.2
        assert trend.time_period == "1h"
        assert trend.prediction == "Expected to stabilize"


class TestDatabaseHealth:
    def test_database_health_creation(self):
        now = datetime.now()
        db_health = DatabaseHealth(
            connected=True,
            response_time_ms=12.5,
            active_connections=5,
            max_connections=100,
            query_performance={'avg': 25.5, 'min': 5.0, 'max': 100.0},
            error_rate=0.01,
            last_backup=now,
            storage_used_mb=512.0
        )
        
        assert db_health.connected == True
        assert db_health.response_time_ms == 12.5
        assert db_health.active_connections == 5
        assert db_health.max_connections == 100
        assert db_health.query_performance['avg'] == 25.5
        assert db_health.error_rate == 0.01
        assert db_health.last_backup == now
        assert db_health.storage_used_mb == 512.0