#!/usr/bin/env python3
"""
Memory Health Monitor - Continuous monitoring for memory endpoint issues
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

class MemoryHealthMonitor:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.log_file = Path("logs/heartbeat_detailed.jsonl")
        
    def check_server_health(self):
        """Check if the server is responding"""
        try:
            response = requests.get(f"{self.base_url}/heartbeat", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_recent_memory_errors(self):
        """Get recent memory-related errors"""
        try:
            response = requests.get(f"{self.base_url}/memory/debug/recent-errors", timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def test_memory_endpoints(self):
        """Test memory endpoints to ensure they're working"""
        results = {}
        
        # Test memory status
        try:
            response = requests.get(f"{self.base_url}/memory/status", timeout=5)
            results['status_endpoint'] = {
                'working': response.status_code == 200,
                'status_code': response.status_code
            }
        except Exception as e:
            results['status_endpoint'] = {
                'working': False,
                'error': str(e)
            }
        
        # Test valid memory store request
        try:
            valid_payload = {
                "memories": [{"content": "Health check memory", "type": "health_check"}],
                "source": "health_monitor"
            }
            response = requests.post(f"{self.base_url}/memory/store", json=valid_payload, timeout=5)
            results['store_endpoint'] = {
                'working': response.status_code == 200,
                'status_code': response.status_code
            }
        except Exception as e:
            results['store_endpoint'] = {
                'working': False,
                'error': str(e)
            }
        
        return results
    
    def analyze_log_patterns(self):
        """Analyze recent log patterns for issues"""
        if not self.log_file.exists():
            return {"error": "Log file not found"}
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-100:] if len(lines) > 100 else lines
            
            memory_requests = 0
            memory_errors = 0
            validation_errors = 0
            
            for line in recent_lines:
                try:
                    log_entry = json.loads(line.strip())
                    
                    # Count memory requests
                    if 'memory' in log_entry.get('data', {}).get('endpoint', '').lower():
                        memory_requests += 1
                    
                    # Count memory errors
                    if (log_entry.get('event_type') == 'error' and 
                        'memory' in str(log_entry).lower()):
                        memory_errors += 1
                    
                    # Count validation errors specifically
                    if (log_entry.get('action') == 'memory_store_validation_error'):
                        validation_errors += 1
                        
                except json.JSONDecodeError:
                    continue
            
            return {
                'recent_memory_requests': memory_requests,
                'recent_memory_errors': memory_errors,
                'recent_validation_errors': validation_errors,
                'error_rate': (memory_errors / memory_requests * 100) if memory_requests > 0 else 0
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze logs: {str(e)}"}
    
    def run_health_check(self):
        """Run comprehensive health check"""
        print("🏥 Memory Health Monitor")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        # Check server health
        server_healthy = self.check_server_health()
        print(f"🌐 Server Health: {'✅ Healthy' if server_healthy else '❌ Down'}")
        
        if not server_healthy:
            print("❌ Server is not responding. Cannot perform further checks.")
            return
        
        # Test endpoints
        print("\n🔧 Endpoint Tests:")
        endpoint_results = self.test_memory_endpoints()
        
        for endpoint, result in endpoint_results.items():
            status = "✅ Working" if result['working'] else "❌ Failed"
            print(f"   {endpoint}: {status}")
            if not result['working'] and 'error' in result:
                print(f"      Error: {result['error']}")
        
        # Check recent errors
        print("\n🚨 Recent Errors:")
        error_data = self.get_recent_memory_errors()
        
        if error_data:
            total_errors = error_data.get('total_errors_found', 0)
            print(f"   Total recent errors: {total_errors}")
            
            if total_errors > 0:
                recent_errors = error_data.get('recent_memory_errors', [])
                if recent_errors:
                    latest = recent_errors[-1]
                    print(f"   Latest error: {latest.get('data', {}).get('error_type', 'unknown')}")
                    print(f"   Request ID: {latest.get('request_id', 'N/A')}")
        else:
            print("   Could not retrieve error data")
        
        # Analyze log patterns
        print("\n📊 Log Analysis:")
        log_analysis = self.analyze_log_patterns()
        
        if 'error' not in log_analysis:
            print(f"   Recent memory requests: {log_analysis['recent_memory_requests']}")
            print(f"   Recent memory errors: {log_analysis['recent_memory_errors']}")
            print(f"   Recent validation errors: {log_analysis['recent_validation_errors']}")
            print(f"   Error rate: {log_analysis['error_rate']:.1f}%")
            
            # Health assessment
            error_rate = log_analysis['error_rate']
            if error_rate == 0:
                print("   📈 Health Status: ✅ Excellent")
            elif error_rate < 5:
                print("   📈 Health Status: ⚠️ Good (minor issues)")
            elif error_rate < 20:
                print("   📈 Health Status: ⚠️ Fair (needs attention)")
            else:
                print("   📈 Health Status: ❌ Poor (immediate attention needed)")
        else:
            print(f"   Error: {log_analysis['error']}")
        
        print("\n💡 Recommendations:")
        if server_healthy and all(r['working'] for r in endpoint_results.values()):
            if log_analysis.get('recent_validation_errors', 0) > 0:
                print("   - Check clients sending requests to /memory/store")
                print("   - Ensure all requests include the 'memories' field")
                print("   - Monitor logs: tail -f logs/heartbeat_detailed.jsonl")
            else:
                print("   - System appears healthy")
                print("   - Continue regular monitoring")
        else:
            print("   - Check server status and endpoint functionality")
            print("   - Review server logs for errors")
    
    def monitor_continuously(self, interval_seconds=60):
        """Run continuous monitoring"""
        print(f"🔄 Starting continuous monitoring (every {interval_seconds}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self.run_health_check()
                print(f"\n⏰ Next check in {interval_seconds} seconds...")
                print("-" * 50)
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")

def main():
    monitor = MemoryHealthMonitor()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        monitor.monitor_continuously(interval)
    else:
        monitor.run_health_check()

if __name__ == "__main__":
    main()