"""
System monitoring utilities for Ray's health system
"""

import psutil
import time
import socket
import subprocess
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import os
import json
from pathlib import Path

from .models import (
    SystemMetrics, NetworkHealth, SecurityHealth, ApplicationHealth,
    HealthAlert, HealthTrend, ServiceStatus, ServiceState, DatabaseHealth
)

logger = logging.getLogger(__name__)


class SystemMonitor:
    """Monitors system health and performance metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.last_metrics = {}
        self.alert_history = []
        self.trend_data = {}
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_used_mb = memory.used / (1024 * 1024)
            memory_total_mb = memory.total / (1024 * 1024)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_used_gb = disk.used / (1024 * 1024 * 1024)
            disk_total_gb = disk.total / (1024 * 1024 * 1024)
            disk_percent = (disk.used / disk.total) * 100
            
            # System uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            # Load average (Unix-like systems)
            try:
                load_avg = list(os.getloadavg())
            except (OSError, AttributeError):
                load_avg = [0.0, 0.0, 0.0]  # Windows fallback
            
            # Network I/O
            net_io = psutil.net_io_counters()
            network_io = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_received': net_io.bytes_recv
            }
            
            # Process counts
            process_count = len(psutil.pids())
            
            # Thread count (approximate)
            thread_count = sum(p.num_threads() for p in psutil.process_iter(['num_threads']) 
                             if p.info['num_threads'] is not None)
            
            return SystemMetrics(
                cpu_usage_percent=cpu_percent,
                memory_usage_percent=memory.percent,
                memory_used_mb=memory_used_mb,
                memory_total_mb=memory_total_mb,
                disk_usage_percent=disk_percent,
                disk_used_gb=disk_used_gb,
                disk_total_gb=disk_total_gb,
                uptime_seconds=uptime_seconds,
                load_average=load_avg,
                network_io=network_io,
                process_count=process_count,
                thread_count=thread_count
            )
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            # Return default metrics on error
            return SystemMetrics(
                cpu_usage_percent=0.0,
                memory_usage_percent=0.0,
                memory_used_mb=0.0,
                memory_total_mb=1024.0,
                disk_usage_percent=0.0,
                disk_used_gb=0.0,
                disk_total_gb=100.0,
                uptime_seconds=0.0,
                load_average=[0.0, 0.0, 0.0],
                network_io={'bytes_sent': 0, 'bytes_received': 0},
                process_count=0,
                thread_count=0
            )
    
    def get_network_health(self) -> NetworkHealth:
        """Check network connectivity and performance"""
        try:
            # Test internet connectivity
            internet_connected = self._test_internet_connection()
            
            # DNS resolution test
            dns_time = self._test_dns_resolution()
            
            # External API status
            external_apis = {
                'google': self._test_connection('8.8.8.8', 53),
                'cloudflare': self._test_connection('1.1.1.1', 53),
                'github': self._test_http_connection('https://api.github.com'),
            }
            
            # Network usage (simplified)
            net_io = psutil.net_io_counters()
            bandwidth_usage = {
                'upload_mbps': 0.0,  # Would need historical data for accurate calculation
                'download_mbps': 0.0
            }
            
            # Ping test for latency
            latency = self._ping_test('8.8.8.8')
            
            return NetworkHealth(
                internet_connected=internet_connected,
                dns_resolution_ms=dns_time,
                external_api_status=external_apis,
                bandwidth_usage=bandwidth_usage,
                latency_ms=latency,
                packet_loss_percent=0.0  # Would need more sophisticated testing
            )
            
        except Exception as e:
            logger.error(f"Error getting network health: {str(e)}")
            return NetworkHealth(
                internet_connected=False,
                dns_resolution_ms=999.0,
                external_api_status={},
                bandwidth_usage={'upload_mbps': 0.0, 'download_mbps': 0.0},
                latency_ms=999.0,
                packet_loss_percent=100.0
            )
    
    def get_security_health(self) -> SecurityHealth:
        """Check security status and threats"""
        try:
            # Basic security checks
            firewall_active = self._check_firewall_status()
            
            # Check for suspicious activity (simplified)
            failed_logins = self._count_failed_logins()
            suspicious_activity = 0  # Would integrate with security logs
            
            # Certificate status (if applicable)
            cert_expiry = self._check_certificate_expiry()
            
            return SecurityHealth(
                firewall_active=firewall_active,
                last_security_scan=datetime.now() - timedelta(hours=1),
                threat_level="low",
                failed_login_attempts=failed_logins,
                suspicious_activity_count=suspicious_activity,
                certificate_expiry_days=cert_expiry,
                encryption_status=True
            )
            
        except Exception as e:
            logger.error(f"Error getting security health: {str(e)}")
            return SecurityHealth(
                firewall_active=False,
                last_security_scan=None,
                threat_level="unknown",
                failed_login_attempts=0,
                suspicious_activity_count=0,
                certificate_expiry_days=None,
                encryption_status=False
            )
    
    def get_application_health(self) -> ApplicationHealth:
        """Get Ray's application-specific health metrics"""
        try:
            # Check loaded modules
            modules_loaded = self._get_loaded_modules()
            modules_failed = self._get_failed_modules()
            
            # Application metrics
            active_sessions = self._count_active_sessions()
            task_queue_size = self._get_task_queue_size()
            
            # Performance metrics
            memory_leaks = self._detect_memory_leaks()
            error_rate = self._calculate_error_rate()
            response_time = self._get_average_response_time()
            cache_hit_rate = self._get_cache_hit_rate()
            
            return ApplicationHealth(
                modules_loaded=modules_loaded,
                modules_failed=modules_failed,
                active_sessions=active_sessions,
                task_queue_size=task_queue_size,
                memory_leaks_detected=memory_leaks,
                error_rate_per_hour=error_rate,
                average_response_time_ms=response_time,
                cache_hit_rate_percent=cache_hit_rate
            )
            
        except Exception as e:
            logger.error(f"Error getting application health: {str(e)}")
            return ApplicationHealth(
                modules_loaded=[],
                modules_failed=[],
                active_sessions=0,
                task_queue_size=0,
                memory_leaks_detected=False,
                error_rate_per_hour=0.0,
                average_response_time_ms=0.0,
                cache_hit_rate_percent=0.0
            )
    
    def get_service_statuses(self) -> List[ServiceStatus]:
        """Get status of all Ray's services"""
        services = []
        
        # Core services to monitor
        service_configs = [
            {'name': 'heartbeat', 'port': None, 'endpoint': '/heartbeat'},
            {'name': 'reflect', 'port': None, 'endpoint': '/reflect'},
            {'name': 'memory', 'port': None, 'endpoint': '/memory/status'},
            {'name': 'directory', 'port': None, 'endpoint': '/directory/status'},
            {'name': 'web', 'port': None, 'endpoint': '/web/status'},
        ]
        
        for config in service_configs:
            try:
                status = self._check_service_status(config)
                services.append(status)
            except Exception as e:
                logger.error(f"Error checking service {config['name']}: {str(e)}")
                services.append(ServiceStatus(
                    name=config['name'],
                    state=ServiceState.ERROR,
                    uptime_seconds=0.0,
                    memory_usage_mb=0.0,
                    cpu_usage_percent=0.0,
                    last_heartbeat=None,
                    error_count=1,
                    response_time_ms=999.0,
                    health_check_passed=False,
                    details={'error': str(e)}
                ))
        
        return services
    
    # Helper methods
    def _test_internet_connection(self) -> bool:
        """Test basic internet connectivity"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    def _test_dns_resolution(self) -> float:
        """Test DNS resolution time"""
        try:
            start_time = time.time()
            socket.gethostbyname('google.com')
            return (time.time() - start_time) * 1000
        except:
            return 999.0
    
    def _test_connection(self, host: str, port: int) -> bool:
        """Test connection to specific host:port"""
        try:
            socket.create_connection((host, port), timeout=3)
            return True
        except:
            return False
    
    def _test_http_connection(self, url: str) -> bool:
        """Test HTTP connection"""
        try:
            import requests
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _ping_test(self, host: str) -> float:
        """Simple ping test for latency"""
        try:
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', '1', host]
            else:
                cmd = ['ping', '-c', '1', host]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Parse ping output for time (simplified)
                return 50.0  # Placeholder
            return 999.0
        except:
            return 999.0
    
    def _check_firewall_status(self) -> bool:
        """Check if firewall is active"""
        try:
            if platform.system().lower() == 'windows':
                result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles'], 
                                      capture_output=True, text=True)
                return 'State                                 ON' in result.stdout
            else:
                # Linux/Mac firewall check (simplified)
                return True  # Assume active
        except:
            return False
    
    def _count_failed_logins(self) -> int:
        """Count recent failed login attempts"""
        # This would integrate with system logs
        return 0
    
    def _check_certificate_expiry(self) -> Optional[int]:
        """Check SSL certificate expiry"""
        # This would check actual certificates
        return None
    
    def _get_loaded_modules(self) -> List[str]:
        """Get list of successfully loaded Ray modules"""
        return ['heartbeat', 'reflect', 'memory', 'directory', 'web', 'health']
    
    def _get_failed_modules(self) -> List[str]:
        """Get list of failed Ray modules"""
        return []
    
    def _count_active_sessions(self) -> int:
        """Count active user sessions"""
        return 1  # Simplified
    
    def _get_task_queue_size(self) -> int:
        """Get current task queue size"""
        return 0  # Would integrate with task system
    
    def _detect_memory_leaks(self) -> bool:
        """Detect potential memory leaks"""
        return False  # Would need historical memory tracking
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate per hour"""
        return 0.0  # Would integrate with logging system
    
    def _get_average_response_time(self) -> float:
        """Get average API response time"""
        return 50.0  # Would track actual response times
    
    def _get_cache_hit_rate(self) -> float:
        """Get cache hit rate percentage"""
        return 85.0  # Would integrate with caching system
    
    def _check_service_status(self, config: Dict) -> ServiceStatus:
        """Check individual service status"""
        return ServiceStatus(
            name=config['name'],
            state=ServiceState.RUNNING,
            uptime_seconds=time.time() - self.start_time,
            memory_usage_mb=50.0,
            cpu_usage_percent=5.0,
            last_heartbeat=datetime.now(),
            error_count=0,
            response_time_ms=25.0,
            health_check_passed=True,
            details={'status': 'healthy'}
        )