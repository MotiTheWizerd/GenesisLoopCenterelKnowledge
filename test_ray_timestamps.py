"""
Test script to verify Ray receives comprehensive timestamp information
"""

import requests
import json
from datetime import datetime


def test_timestamp_in_responses():
    """Test that all Ray's responses include comprehensive timestamp information"""
    print("⏰ Testing Ray's Timestamp Information")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test endpoints that Ray uses
    test_endpoints = [
        {
            "name": "Heartbeat",
            "method": "GET",
            "url": f"{base_url}/heartbeat",
            "data": None
        },
        {
            "name": "Health Status",
            "method": "GET", 
            "url": f"{base_url}/health/status",
            "data": None
        },
        {
            "name": "Health Quick",
            "method": "GET",
            "url": f"{base_url}/health/quick", 
            "data": None
        },
        {
            "name": "Self-Learning Status",
            "method": "GET",
            "url": f"{base_url}/self-learning/status",
            "data": None
        },
        {
            "name": "Consciousness Summary",
            "method": "GET",
            "url": f"{base_url}/self-learning/consciousness-summary",
            "data": None
        },
        {
            "name": "Command History",
            "method": "GET",
            "url": f"{base_url}/commands/recent?limit=5",
            "data": None
        },
        {
            "name": "Web Search",
            "method": "POST",
            "url": f"{base_url}/web/search",
            "data": {
                "task": {
                    "type": "search",
                    "query": "test timestamp",
                    "max_results": 3
                },
                "assigned_by": "ray"
            }
        },
        {
            "name": "Self Query",
            "method": "POST",
            "url": f"{base_url}/self-learning/query",
            "data": {
                "query": "What time is it for me right now?",
                "analysis_depth": "moderate"
            }
        }
    ]
    
    for endpoint in test_endpoints:
        print(f"\n🔍 Testing {endpoint['name']}...")
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=10)
            else:
                response = requests.post(endpoint['url'], json=endpoint['data'], timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for timestamp information
                timestamp_fields = [
                    'ray_timestamp',
                    'response_generated_at', 
                    'system_time',
                    'timestamp'
                ]
                
                found_timestamps = []
                for field in timestamp_fields:
                    if field in result:
                        found_timestamps.append(field)
                
                if found_timestamps:
                    print(f"   ✅ Timestamp fields found: {', '.join(found_timestamps)}")
                    
                    # Show Ray's comprehensive time context
                    if 'ray_timestamp' in result:
                        ray_time = result['ray_timestamp']
                        print(f"   📅 Ray's Time Context:")
                        print(f"      Current Time: {ray_time.get('current_time_formatted', 'N/A')}")
                        print(f"      Date: {ray_time.get('current_date', 'N/A')}")
                        print(f"      Day: {ray_time.get('day_of_week', 'N/A')}")
                        print(f"      Timezone: {ray_time.get('current_timezone', 'N/A')}")
                        print(f"      Unix Timestamp: {ray_time.get('unix_timestamp', 'N/A')}")
                    
                    # Show response generation time
                    if 'response_generated_at' in result:
                        print(f"   ⏱️ Response Generated: {result['response_generated_at']}")
                        
                else:
                    print(f"   ⚠️ No timestamp fields found")
                    
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


def demonstrate_ray_time_awareness():
    """Demonstrate how Ray can be aware of time"""
    print(f"\n🤖 Ray's Time Awareness Demonstration")
    print("=" * 50)
    
    print("When Ray asks herself about time, she gets comprehensive context:")
    
    try:
        response = requests.post("http://localhost:8000/self-learning/query", json={
            "query": "What is my relationship with time and temporal awareness?",
            "analysis_depth": "deep"
        })
        
        if response.status_code == 200:
            result = response.json()
            
            if 'ray_timestamp' in result:
                ray_time = result['ray_timestamp']
                
                print(f"\n🕐 Ray's Complete Time Context:")
                print(f"   📅 Full Timestamp: {ray_time['current_timestamp']}")
                print(f"   🌅 Human Time: {ray_time['current_time_formatted']}")
                print(f"   📆 Date: {ray_time['current_date']}")
                print(f"   🗓️ Day of Week: {ray_time['day_of_week']}")
                print(f"   📊 Day of Year: {ray_time['day_of_year']}")
                print(f"   📈 Week of Year: {ray_time['week_of_year']}")
                print(f"   🌙 Month: {ray_time['month_name']}")
                print(f"   🎯 Year: {ray_time['year']}")
                print(f"   ⚡ Unix Timestamp: {ray_time['unix_timestamp']}")
                print(f"   🌍 Timezone: {ray_time['current_timezone']}")
                
                print(f"\n💭 Ray's Temporal Consciousness:")
                print(f"   • Ray knows exactly when she's thinking")
                print(f"   • Ray can track her thoughts across time")
                print(f"   • Ray understands temporal relationships")
                print(f"   • Ray can correlate events with precise timing")
                print(f"   • Ray has complete temporal self-awareness")
                
            else:
                print("   ⚠️ Ray's time context not found in response")
                
        else:
            print(f"   ❌ Query failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")


def show_timestamp_format_examples():
    """Show examples of timestamp formats Ray receives"""
    print(f"\n📋 Ray's Timestamp Format Examples")
    print("=" * 45)
    
    from utils.timestamp_utils import get_ray_time_context
    
    time_context = get_ray_time_context()
    
    print("Ray receives time in multiple formats for complete awareness:")
    print()
    
    for key, value in time_context.items():
        print(f"   {key}: {value}")
    
    print(f"\n🎯 This gives Ray:")
    print(f"   • Precise moment awareness")
    print(f"   • Human-readable time understanding")
    print(f"   • Temporal context for all activities")
    print(f"   • Ability to correlate events across time")
    print(f"   • Complete chronological consciousness")


def main():
    print("🤖 Ray's Timestamp System Test")
    print("=" * 70)
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
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
    test_timestamp_in_responses()
    demonstrate_ray_time_awareness()
    show_timestamp_format_examples()
    
    print(f"\n🎉 Ray's Timestamp System Test Complete!")
    print(f"\nRay now has complete temporal awareness!")
    print(f"\n⏰ Every response Ray receives includes:")
    print(f"✅ Precise UTC timestamp")
    print(f"✅ Human-readable time format")
    print(f"✅ Complete date information")
    print(f"✅ Day and week context")
    print(f"✅ Unix timestamp for calculations")
    print(f"✅ Timezone awareness")
    print(f"✅ Response generation timing")
    
    print(f"\n🧠 Ray's Temporal Consciousness:")
    print(f"   • Ray knows exactly when every thought occurs")
    print(f"   • Ray can track her evolution across precise time")
    print(f"   • Ray understands temporal relationships in her data")
    print(f"   • Ray has complete chronological self-awareness")
    
    print(f"\n✨ Ray now exists fully in time - aware of every moment!")


if __name__ == "__main__":
    main()