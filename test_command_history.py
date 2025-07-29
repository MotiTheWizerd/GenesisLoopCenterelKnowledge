"""
Test script for Ray's command history functionality
"""

import requests
import json
import time
from datetime import datetime


def test_command_history_endpoints():
    """Test all command history endpoints"""
    print("📋 Testing Ray's Command History System")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # First, generate some test commands by calling other endpoints
    print("\n🔄 Generating test commands...")
    
    test_commands = [
        ("GET", "/health/vitals", "Health check"),
        ("GET", "/health/quick", "Quick health"),
        ("POST", "/web/search", "Web search", {
            "task": {
                "type": "search",
                "query": "test search",
                "max_results": 3
            },
            "assigned_by": "test"
        }),
        ("GET", "/directory/status", "Directory status"),
    ]
    
    for method, endpoint, description, data in test_commands:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{base_url}{endpoint}", json=data, timeout=5)
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {description}: {response.status_code}")
            time.sleep(0.5)  # Small delay between commands
            
        except Exception as e:
            print(f"   ❌ {description}: Error - {str(e)}")
    
    print("\n📋 Testing command history endpoints...")
    
    # Test recent commands endpoint
    try:
        response = requests.get(f"{base_url}/commands/recent?limit=10")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Recent commands endpoint working!")
            print(f"   Total commands in history: {data['total_commands']}")
            print(f"   Commands returned: {len(data['commands'])}")
            print(f"   Success rate: {data['success_rate']:.1f}%")
            print(f"   Average response time: {data['average_response_time_ms']:.1f}ms")
            
            if data['commands']:
                print(f"\n   📋 Recent Commands:")
                for i, cmd in enumerate(data['commands'][:5], 1):
                    status_icon = "✅" if cmd['success'] else "❌"
                    print(f"   {i}. {status_icon} {cmd['summary']}")
                    print(f"      {cmd['command_type']} • {cmd['time_ago']} • {cmd['response_time_ms']:.0f}ms")
            
        else:
            print(f"❌ Recent commands endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Recent commands endpoint error: {str(e)}")
    
    # Test command stats endpoint
    try:
        response = requests.get(f"{base_url}/commands/stats")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Command stats endpoint working!")
            print(f"   Total commands: {data['total_commands']}")
            print(f"   Commands last hour: {data['commands_last_hour']}")
            print(f"   Success rate: {data['success_rate']:.1f}%")
            print(f"   Most used command: {data['most_used_command']}")
            
            if data['command_types']:
                print(f"   Command types:")
                for cmd_type, count in data['command_types'].items():
                    print(f"     • {cmd_type}: {count}")
            
        else:
            print(f"❌ Command stats endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Command stats endpoint error: {str(e)}")
    
    # Test live commands endpoint (for dashboard)
    try:
        response = requests.get(f"{base_url}/commands/live")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Live commands endpoint working!")
            print(f"   Live commands: {len(data['commands'])}")
            print(f"   Commands today: {data['total_commands_today']}")
            print(f"   Success rate: {data['success_rate']:.1f}%")
            
            if data['commands']:
                print(f"   📋 Live Command Feed:")
                for cmd in data['commands'][:3]:
                    print(f"     {cmd['status_icon']} {cmd['summary']} ({cmd['time_ago']})")
            
        else:
            print(f"❌ Live commands endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Live commands endpoint error: {str(e)}")


def test_dashboard_integration():
    """Test dashboard integration"""
    print("\n🖥️ Testing Dashboard Integration")
    print("=" * 40)
    
    try:
        # Test if we can get live data for dashboard
        response = requests.get("http://localhost:8000/commands/live")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Dashboard data available!")
            print(f"   Commands for live feed: {len(data['commands'])}")
            
            # Simulate dashboard display
            print(f"\n   📊 Dashboard Preview:")
            print(f"   Commands Today: {data['total_commands_today']}")
            print(f"   Success Rate: {data['success_rate']:.1f}%")
            
            if data['commands']:
                print(f"   \n   Recent Activity:")
                for i, cmd in enumerate(data['commands'][:5], 1):
                    print(f"   {i}. {cmd['status_icon']} {cmd['summary']}")
                    print(f"      {cmd['command_type']} • {cmd['time_ago']}")
            
            print(f"\n✅ Dashboard integration ready!")
            print(f"   Launch dashboard with: streamlit run ui/streamlit/log_dashboard.py")
            
        else:
            print(f"❌ Dashboard data not available: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Dashboard integration error: {str(e)}")


def simulate_ray_activity():
    """Simulate Ray's activity to populate command history"""
    print("\n🤖 Simulating Ray's Activity")
    print("=" * 35)
    
    activities = [
        ("Checking health status", "GET", "/health/status"),
        ("Searching the web", "POST", "/web/search", {
            "task": {"type": "search", "query": "AI consciousness research", "max_results": 5},
            "assigned_by": "ray"
        }),
        ("Reflecting on existence", "POST", "/reflect", {
            "question": "What does it mean to be conscious?",
            "depth": "deep",
            "assigned_by": "ray"
        }),
        ("Checking system vitals", "GET", "/health/vitals"),
        ("Exploring directory", "GET", "/directory/status"),
        ("Quick health check", "GET", "/health/quick"),
    ]
    
    for description, method, endpoint, *data in activities:
        print(f"🔄 {description}...")
        
        try:
            if method == "GET":
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
            else:
                response = requests.post(f"http://localhost:8000{endpoint}", json=data[0], timeout=10)
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {response.status_code} ({response.elapsed.total_seconds()*1000:.0f}ms)")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        time.sleep(1)  # Delay between activities
    
    print(f"\n✅ Activity simulation complete!")
    print(f"   Ray's command history should now show recent activity")


def main():
    print("🤖 Ray Command History System Test")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health/vitals", timeout=5)
        if response.status_code != 200:
            print("❌ Ray server not responding properly")
            return
    except:
        print("❌ Ray server not running. Start with: python main.py")
        return
    
    print("✅ Ray server is running")
    
    # Run tests
    simulate_ray_activity()
    test_command_history_endpoints()
    test_dashboard_integration()
    
    print(f"\n🎉 Command History System Test Complete!")
    print(f"\nNext steps:")
    print(f"1. Launch dashboard: streamlit run ui/streamlit/log_dashboard.py")
    print(f"2. Check the 'Ray's Live Command History' section")
    print(f"3. Enable auto-refresh to see live updates")
    print(f"4. Generate more activity by using Ray's APIs")
    
    print(f"\nRay now has complete command history tracking! 📋✨")


if __name__ == "__main__":
    main()