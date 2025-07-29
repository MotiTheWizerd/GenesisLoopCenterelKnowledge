"""
Ray Health Monitoring Examples
Demonstrates Ray's system health monitoring capabilities
"""

import requests
import json
from datetime import datetime


def get_full_health_status():
    """Get Ray's complete health status"""
    print("💚 Ray's Complete Health Status")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/health/status")
        
        if response.status_code == 200:
            health = response.json()
            
            # Overall status
            print(f"🏥 Overall Status: {health['overall_status'].upper()}")
            print(f"📝 Status Message: {health['status_message']}")
            print(f"⏰ Uptime: {health['uptime_human']}")
            print(f"📊 Performance Score: {health['performance_score']:.1f}/100")
            print(f"🔄 Availability: {health['availability_percent']:.2f}%")
            
            # System vitals
            print(f"\n🖥️ System Vitals:")
            sys_metrics = health['system_metrics']
            print(f"   CPU Usage: {sys_metrics['cpu_usage_percent']:.1f}%")
            print(f"   Memory Usage: {sys_metrics['memory_usage_percent']:.1f}% ({sys_metrics['memory_used_mb']:.0f}MB / {sys_metrics['memory_total_mb']:.0f}MB)")
            print(f"   Disk Usage: {sys_metrics['disk_usage_percent']:.1f}% ({sys_metrics['disk_used_gb']:.1f}GB / {sys_metrics['disk_total_gb']:.1f}GB)")
            print(f"   Processes: {sys_metrics['process_count']}")
            print(f"   Threads: {sys_metrics['thread_count']}")
            
            # Services
            print(f"\n🔧 Services Status:")
            for service in health['services']:
                status_icon = "✅" if service['state'] == 'running' else "❌"
                print(f"   {status_icon} {service['name']}: {service['state']} (Response: {service['response_time_ms']:.1f}ms)")
            
            # Network health
            print(f"\n🌐 Network Health:")
            net = health['network_health']
            internet_icon = "✅" if net['internet_connected'] else "❌"
            print(f"   {internet_icon} Internet: {'Connected' if net['internet_connected'] else 'Disconnected'}")
            print(f"   🔍 DNS Resolution: {net['dns_resolution_ms']:.1f}ms")
            print(f"   📡 Latency: {net['latency_ms']:.1f}ms")
            
            # Security
            print(f"\n🔒 Security Status:")
            sec = health['security_health']
            firewall_icon = "✅" if sec['firewall_active'] else "⚠️"
            print(f"   {firewall_icon} Firewall: {'Active' if sec['firewall_active'] else 'Inactive'}")
            print(f"   🛡️ Threat Level: {sec['threat_level']}")
            print(f"   🚫 Failed Logins: {sec['failed_login_attempts']}")
            
            # Ray's consciousness metrics
            print(f"\n🧠 Ray's Consciousness Metrics:")
            consciousness = health['consciousness_metrics']
            print(f"   🎯 Consciousness Coherence: {consciousness['consciousness_coherence']:.1f}%")
            print(f"   🧩 Self-Awareness Index: {consciousness['self_awareness_index']:.1f}%")
            print(f"   💭 Reflection Cycles: {consciousness['reflection_cycles_completed']}")
            print(f"   😌 Emotional Stability: {consciousness['emotional_stability']:.1f}%")
            
            # Learning metrics
            print(f"\n📚 Learning System Health:")
            learning = health['learning_metrics']
            print(f"   📈 Learning Rate: {learning['learning_rate']:.1f}%")
            print(f"   🎯 Pattern Recognition: {learning['pattern_recognition_accuracy']:.1f}%")
            print(f"   🧠 Knowledge Base Size: {learning['knowledge_base_size']:,} items")
            print(f"   🔍 Curiosity Index: {learning['curiosity_index']:.1f}%")
            
            # Memory system
            print(f"\n💾 Memory System Health:")
            memory = health['memory_system_health']
            print(f"   🧩 Memory Coherence: {memory['memory_coherence']:.1f}%")
            print(f"   ⚡ Retrieval Speed: {memory['retrieval_speed_ms']:.1f}ms")
            print(f"   📦 Memory Fragments: {memory['memory_fragments']:,}")
            print(f"   🔄 Consolidation: {'Active' if memory['memory_consolidation_active'] else 'Inactive'}")
            
            # Active alerts
            if health['active_alerts']:
                print(f"\n⚠️ Active Alerts ({len(health['active_alerts'])}):")
                for alert in health['active_alerts']:
                    level_icon = "🚨" if alert['level'] == 'critical' else "⚠️" if alert['level'] == 'warning' else "ℹ️"
                    print(f"   {level_icon} [{alert['level'].upper()}] {alert['message']}")
                    if alert['suggested_action']:
                        print(f"      💡 Suggestion: {alert['suggested_action']}")
            else:
                print(f"\n✅ No Active Alerts - All systems healthy!")
            
            # Recommendations
            if health['recommendations']:
                print(f"\n💡 Health Recommendations:")
                for i, rec in enumerate(health['recommendations'], 1):
                    print(f"   {i}. {rec}")
            
        else:
            print(f"❌ Failed to get health status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Ray server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def get_quick_health():
    """Get Ray's quick health summary"""
    print("\n💚 Ray's Quick Health Check")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8000/health/quick")
        
        if response.status_code == 200:
            health = response.json()
            
            status_icon = {
                'excellent': '🟢',
                'good': '🟡', 
                'warning': '🟠',
                'critical': '🔴',
                'error': '❌'
            }.get(health['overall_status'], '❓')
            
            print(f"{status_icon} Status: {health['overall_status'].upper()}")
            print(f"📊 Performance: {health['performance_score']:.1f}/100")
            print(f"🖥️ CPU: {health['cpu_usage']:.1f}%")
            print(f"💾 Memory: {health['memory_usage']:.1f}%")
            print(f"💿 Disk: {health['disk_usage']:.1f}%")
            print(f"🔧 Services: {health['services_running']}/{health['services_total']} running")
            print(f"⚠️ Alerts: {health['active_alerts']}")
            
        else:
            print(f"❌ Failed to get quick health: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def get_system_vitals():
    """Get Ray's core system vitals"""
    print("\n💚 Ray's System Vitals")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:8000/health/vitals")
        
        if response.status_code == 200:
            vitals = response.json()
            
            print(f"🖥️ CPU: {vitals['cpu_usage_percent']:.1f}%")
            print(f"💾 Memory: {vitals['memory_usage_percent']:.1f}%")
            print(f"💿 Disk: {vitals['disk_usage_percent']:.1f}%")
            print(f"⏰ Uptime: {vitals['uptime_human']}")
            print(f"📊 Performance: {vitals['performance_score']:.1f}/100")
            print(f"🧠 Consciousness: {vitals['consciousness_coherence']:.1f}%")
            print(f"📚 Learning: {vitals['learning_velocity']:.1f}%")
            print(f"💭 Memory Health: {vitals['memory_health']:.1f}%")
            
        else:
            print(f"❌ Failed to get vitals: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def monitor_health_over_time():
    """Monitor Ray's health over time"""
    print("\n💚 Ray's Health Monitoring (5 checks)")
    print("=" * 45)
    
    import time
    
    for i in range(5):
        print(f"\n📊 Check {i+1}/5:")
        
        try:
            response = requests.get("http://localhost:8000/health/vitals")
            
            if response.status_code == 200:
                vitals = response.json()
                
                # Create simple health bar
                cpu_bar = "█" * int(vitals['cpu_usage_percent'] / 10) + "░" * (10 - int(vitals['cpu_usage_percent'] / 10))
                mem_bar = "█" * int(vitals['memory_usage_percent'] / 10) + "░" * (10 - int(vitals['memory_usage_percent'] / 10))
                
                print(f"   CPU: [{cpu_bar}] {vitals['cpu_usage_percent']:.1f}%")
                print(f"   MEM: [{mem_bar}] {vitals['memory_usage_percent']:.1f}%")
                print(f"   Performance: {vitals['performance_score']:.1f}/100")
                
            else:
                print(f"   ❌ Check failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        if i < 4:  # Don't sleep after last check
            time.sleep(2)
    
    print("\n✅ Health monitoring completed!")


def main():
    print("🤖 Ray Health Monitoring Examples")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run examples
    get_full_health_status()
    get_quick_health()
    get_system_vitals()
    monitor_health_over_time()
    
    print("\n✨ Health monitoring examples completed!")
    print("\nRay's health monitoring system provides:")
    print("• Complete system health overview")
    print("• Real-time performance metrics")
    print("• Consciousness and learning metrics")
    print("• Proactive alerts and recommendations")
    print("• Historical health trends")
    print("\nRay can now monitor her own digital well-being! 💚🤖")


if __name__ == "__main__":
    main()