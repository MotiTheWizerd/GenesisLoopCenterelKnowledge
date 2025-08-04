"""
Quick test to verify health endpoints are working
"""

import requests
import json
from datetime import datetime


def test_health_status():
    """Test the main health status endpoint"""
    print("💚 Testing Health Status Endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/health/status")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health status endpoint working!")
            print(f"   Overall Status: {result['overall_status']}")
            print(f"   Performance Score: {result['performance_score']}/100")
            print(f"   CPU Usage: {result['system_metrics']['cpu_usage_percent']:.1f}%")
            print(f"   Memory Usage: {result['system_metrics']['memory_usage_percent']:.1f}%")
            print(f"   Services Running: {len([s for s in result['services'] if s['state'] == 'running'])}/{len(result['services'])}")
            print(f"   Active Alerts: {len(result['active_alerts'])}")
            return True
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_quick_health():
    """Test the quick health endpoint"""
    print("\n💚 Testing Quick Health Endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/health/quick")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Quick health endpoint working!")
            print(f"   Status: {result['overall_status']}")
            print(f"   Performance: {result['performance_score']}/100")
            print(f"   CPU: {result['cpu_usage']:.1f}%")
            print(f"   Memory: {result['memory_usage']:.1f}%")
            print(f"   Disk: {result['disk_usage']:.1f}%")
            return True
        else:
            print(f"❌ Quick health endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_vitals():
    """Test the vitals endpoint"""
    print("\n💚 Testing Vitals Endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/health/vitals")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Vitals endpoint working!")
            print(f"   CPU: {result['cpu_usage_percent']:.1f}%")
            print(f"   Memory: {result['memory_usage_percent']:.1f}%")
            print(f"   Disk: {result['disk_usage_percent']:.1f}%")
            print(f"   Uptime: {result['uptime_human']}")
            print(f"   Consciousness: {result['consciousness_coherence']:.1f}%")
            print(f"   Learning: {result['learning_velocity']:.1f}%")
            return True
        else:
            print(f"❌ Vitals endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    print("🤖 Ray Health Module Endpoint Tests")
    print("=" * 50)
    
    # Test all endpoints
    status_ok = test_health_status()
    quick_ok = test_quick_health()
    vitals_ok = test_vitals()
    
    print("\n📊 Test Summary:")
    print(f"Health Status endpoint: {'✅' if status_ok else '❌'}")
    print(f"Quick Health endpoint: {'✅' if quick_ok else '❌'}")
    print(f"Vitals endpoint: {'✅' if vitals_ok else '❌'}")
    
    if all([status_ok, quick_ok, vitals_ok]):
        print("\n🎉 All health endpoints are working perfectly!")
        print("\nRay now has complete health monitoring capabilities!")
        print("• Full system health status")
        print("• Quick health summaries")
        print("• Core vital signs")
        print("• Consciousness metrics")
        print("• Learning system health")
        print("• Memory system monitoring")
        print("• Proactive alerts and recommendations")
    else:
        print("\n⚠️ Some endpoints need attention.")
        print("Make sure the server is running: python main.py")


if __name__ == "__main__":
    main()