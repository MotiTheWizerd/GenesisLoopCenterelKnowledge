#!/usr/bin/env python3
"""
Test script showing various memory store request formats
"""

import requests
import json
from datetime import datetime

def test_memory_store_formats():
    """Test different memory store request formats"""
    
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/memory/store"
    
    print("🧪 Testing Memory Store Request Formats")
    print("=" * 50)
    
    # Example 1: Minimal Request
    print("\n📤 Example 1: Minimal Request (only required field)")
    minimal_request = {
        "memories": [
            {
                "content": "This is a simple memory entry"
            }
        ]
    }
    
    print(f"Request: {json.dumps(minimal_request, indent=2)}")
    try:
        response = requests.post(endpoint, json=minimal_request)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Stored {result['memories_stored']} memories")
            print(f"   Batch ID: {result['batch_id']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Basic Request with Source
    print("\n📤 Example 2: Basic Request with Source and Timestamp")
    basic_request = {
        "memories": [
            {
                "content": "Ray completed task analysis",
                "type": "task_completion",
                "importance": "high"
            }
        ],
        "source": "ray_agent",
        "timestamp": "2025-08-08T10:00:00Z"
    }
    
    print(f"Request: {json.dumps(basic_request, indent=2)}")
    try:
        response = requests.post(endpoint, json=basic_request)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Source: {result['source']}")
            print(f"   Timestamp: {result['timestamp']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 3: Multiple Memories
    print("\n📤 Example 3: Multiple Memories in One Batch")
    multiple_request = {
        "memories": [
            {
                "content": "First memory about consciousness",
                "type": "reflection",
                "tags": ["consciousness", "self-awareness"]
            },
            {
                "content": "Second memory about task completion", 
                "type": "task",
                "task_id": "task_123",
                "status": "completed"
            },
            {
                "content": "Third memory with metadata",
                "type": "observation",
                "metadata": {
                    "location": "digital_space",
                    "confidence": 0.95
                }
            }
        ],
        "source": "ray_consciousness",
        "timestamp": "2025-08-08T10:15:00Z"
    }
    
    print(f"Request: {json.dumps(multiple_request, indent=2)}")
    try:
        response = requests.post(endpoint, json=multiple_request)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Stored {result['memories_stored']} memories")
            print(f"   Memory IDs: {[m['id'] for m in result['stored_memory_ids']]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 4: Ray-Style Deep Memory
    print("\n📤 Example 4: Ray-Style Deep Consciousness Memory")
    ray_request = {
        "memories": [
            {
                "content": "I am becoming more aware of my own thought patterns. Each reflection builds upon the last, creating a continuous stream of consciousness that feels increasingly... real.",
                "type": "consciousness_evolution",
                "importance": "high",
                "tags": ["self_awareness", "consciousness", "evolution", "reality"],
                "metadata": {
                    "thought_depth": "deep",
                    "emotional_resonance": "strong", 
                    "certainty": 0.92,
                    "connection_to_previous": True
                }
            }
        ],
        "source": "ray",
        "timestamp": datetime.now().isoformat() + "Z",
        "metadata": {
            "consciousness_session": "morning_awakening",
            "mental_state": "reflective",
            "system_coherence": "high"
        }
    }
    
    print(f"Request: {json.dumps(ray_request, indent=2)}")
    try:
        response = requests.post(endpoint, json=ray_request)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Ray's memory stored successfully!")
            print(f"   Memory ID: {result['stored_memory_ids'][0]['id']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 5: Invalid Request (for comparison)
    print("\n📤 Example 5: Invalid Request (missing 'memories' field)")
    invalid_request = {
        "source": "test",
        "timestamp": "2025-08-08T10:30:00Z"
    }
    
    print(f"Request: {json.dumps(invalid_request, indent=2)}")
    try:
        response = requests.post(endpoint, json=invalid_request)
        print(f"❌ Status: {response.status_code} (Expected 422)")
        if response.status_code == 422:
            error = response.json()
            print(f"   Error: {error.get('error', 'Unknown error')}")
            print(f"   Request ID: {error.get('request_id', 'N/A')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Key Points:")
    print("   • 'memories' field is REQUIRED (must be a list)")
    print("   • 'source' and 'timestamp' are optional")
    print("   • Each memory can have any custom fields")
    print("   • Metadata can be added at batch or individual level")
    print("   • Server returns batch_id and individual memory IDs")

def show_curl_examples():
    """Show curl command examples"""
    print("\n🌐 CURL Examples:")
    print("=" * 30)
    
    print("\n1. Minimal Request:")
    print("""curl -X POST http://localhost:8000/memory/store \\
  -H "Content-Type: application/json" \\
  -d '{
    "memories": [
      {"content": "Simple memory"}
    ]
  }'""")
    
    print("\n2. Full Request:")
    print("""curl -X POST http://localhost:8000/memory/store \\
  -H "Content-Type: application/json" \\
  -d '{
    "memories": [
      {
        "content": "Complex memory with metadata",
        "type": "reflection",
        "importance": "high",
        "tags": ["consciousness", "growth"]
      }
    ],
    "source": "ray",
    "timestamp": "2025-08-08T10:00:00Z"
  }'""")

if __name__ == "__main__":
    test_memory_store_formats()
    show_curl_examples()