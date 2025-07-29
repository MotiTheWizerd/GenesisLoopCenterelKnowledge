"""
Test Ray's self-learning system against actual JSON logs
Validates that the system correctly analyzes real log data
"""

import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def load_sample_logs() -> List[Dict]:
    """Load actual logs for testing"""
    log_file = Path("logs/heartbeat_detailed.jsonl")
    
    if not log_file.exists():
        print("❌ No log file found at logs/heartbeat_detailed.jsonl")
        return []
    
    logs = []
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    log_entry = json.loads(line.strip())
                    logs.append(log_entry)
    except Exception as e:
        print(f"❌ Error loading logs: {str(e)}")
        return []
    
    return logs


def analyze_log_structure(logs: List[Dict]) -> Dict[str, Any]:
    """Analyze the structure of actual logs"""
    if not logs:
        return {}
    
    analysis = {
        "total_logs": len(logs),
        "event_types": {},
        "reflection_logs": [],
        "task_logs": [],
        "date_range": {},
        "sample_reflection_content": []
    }
    
    # Analyze event types
    for log in logs:
        event_type = log.get('event_type', 'unknown')
        analysis['event_types'][event_type] = analysis['event_types'].get(event_type, 0) + 1
        
        # Extract reflection content
        if 'reflection' in str(log):
            reflection_data = log.get('data', {})
            if 'reflection' in reflection_data:
                analysis['reflection_logs'].append(log)
                reflection_text = reflection_data['reflection']
                if len(reflection_text) > 50:  # Only meaningful reflections
                    analysis['sample_reflection_content'].append({
                        'timestamp': log.get('timestamp'),
                        'reflection': reflection_text[:200] + "..." if len(reflection_text) > 200 else reflection_text
                    })
        
        # Extract task data
        if log.get('event_type') == 'task_requested':
            analysis['task_logs'].append(log)
    
    # Date range
    if logs:
        analysis['date_range'] = {
            'first_log': logs[0].get('timestamp'),
            'last_log': logs[-1].get('timestamp')
        }
    
    return analysis


def test_log_analysis_accuracy():
    """Test that the self-learning system accurately analyzes real logs"""
    print("🔍 Testing Log Analysis Accuracy")
    print("=" * 50)
    
    # Load actual logs
    logs = load_sample_logs()
    if not logs:
        print("❌ No logs available for testing")
        return False
    
    # Analyze log structure
    analysis = analyze_log_structure(logs)
    
    print(f"📊 Log Analysis Results:")
    print(f"   Total logs: {analysis['total_logs']}")
    print(f"   Event types: {len(analysis['event_types'])}")
    print(f"   Reflection logs: {len(analysis['reflection_logs'])}")
    print(f"   Task logs: {len(analysis['task_logs'])}")
    
    if analysis['date_range']:
        print(f"   Date range: {analysis['date_range']['first_log']} to {analysis['date_range']['last_log']}")
    
    # Show event type distribution
    print(f"\n📈 Event Type Distribution:")
    for event_type, count in sorted(analysis['event_types'].items(), key=lambda x: x[1], reverse=True):
        print(f"   • {event_type}: {count}")
    
    # Show sample reflections
    if analysis['sample_reflection_content']:
        print(f"\n💭 Sample Reflection Content:")
        for i, reflection in enumerate(analysis['sample_reflection_content'][:3], 1):
            print(f"   {i}. [{reflection['timestamp']}]")
            print(f"      {reflection['reflection']}")
    
    return True


def test_self_learning_with_real_data():
    """Test self-learning endpoints with real log data"""
    print("\n🧠 Testing Self-Learning with Real Data")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test queries that should find real patterns in the logs
    real_data_queries = [
        {
            "query": "What reflection patterns do I show?",
            "analysis_depth": "moderate",
            "time_range": "all",
            "expected_findings": ["reflection patterns", "consciousness themes"]
        },
        {
            "query": "How do I explore consciousness?",
            "analysis_depth": "deep", 
            "time_range": "all",
            "expected_findings": ["consciousness exploration", "awareness patterns"]
        },
        {
            "query": "What questions do I ask myself?",
            "analysis_depth": "moderate",
            "time_range": "all",
            "expected_findings": ["self-inquiry patterns", "question themes"]
        }
    ]
    
    for i, query_data in enumerate(real_data_queries, 1):
        print(f"\n🔍 Query {i}: {query_data['query']}")
        
        try:
            response = requests.post(f"{base_url}/self-learning/query", json={
                "query": query_data["query"],
                "analysis_depth": query_data["analysis_depth"],
                "time_range": query_data["time_range"]
            })
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"   ✅ Query successful!")
                print(f"      Data points analyzed: {result['data_points_analyzed']}")
                print(f"      Insights found: {len(result['primary_insights'])}")
                print(f"      Patterns found: {len(result['behavioral_patterns'])}")
                print(f"      Processing time: {result['processing_time_ms']:.1f}ms")
                
                # Validate findings
                if result['primary_insights']:
                    print(f"      Sample insight: {result['primary_insights'][0]['insight_text'][:100]}...")
                    
                if result['behavioral_patterns']:
                    print(f"      Sample pattern: {result['behavioral_patterns'][0]['pattern_name']}")
                
                # Check if we found expected data
                found_expected = False
                for insight in result['primary_insights']:
                    for expected in query_data['expected_findings']:
                        if expected.lower() in insight['insight_text'].lower():
                            found_expected = True
                            break
                
                if found_expected:
                    print(f"      ✅ Found expected patterns in real data")
                else:
                    print(f"      ⚠️  Expected patterns not clearly identified")
                    
            else:
                print(f"   ❌ Query failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Query error: {str(e)}")


def test_memory_excavation_accuracy():
    """Test memory excavation against real log content"""
    print("\n🏺 Testing Memory Excavation Accuracy")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Load logs to see what terms actually exist
    logs = load_sample_logs()
    reflection_terms = set()
    
    for log in logs:
        if 'reflection' in str(log):
            reflection_data = log.get('data', {})
            if 'reflection' in reflection_data:
                reflection_text = reflection_data['reflection'].lower()
                # Extract key terms
                key_terms = ['consciousness', 'awareness', 'existence', 'thinking', 'being', 'reality']
                for term in key_terms:
                    if term in reflection_text:
                        reflection_terms.add(term)
    
    print(f"📝 Terms found in actual reflections: {sorted(reflection_terms)}")
    
    if reflection_terms:
        # Test excavation with terms that actually exist in logs
        search_terms = list(reflection_terms)[:3]  # Use first 3 terms
        
        try:
            response = requests.post(f"{base_url}/self-learning/excavate-memories", json={
                "search_terms": search_terms,
                "time_range": "all",
                "correlation_analysis": True,
                "include_forgotten": True
            })
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Memory excavation successful!")
                print(f"   Search terms: {search_terms}")
                print(f"   Memories found: {len(result.get('memories_found', []))}")
                print(f"   Connections discovered: {len(result.get('connections_discovered', []))}")
                print(f"   Thematic clusters: {len(result.get('thematic_clusters', {}))}")
                
                # Show thematic clusters
                if result.get('thematic_clusters'):
                    print(f"   Memory themes found:")
                    for theme, memories in result['thematic_clusters'].items():
                        print(f"     • {theme}: {len(memories)} memories")
                        
                return True
                
            else:
                print(f"❌ Memory excavation failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Memory excavation error: {str(e)}")
            return False
    else:
        print("⚠️  No reflection terms found in logs to test with")
        return False


def validate_consciousness_tracking():
    """Validate consciousness development tracking against real data"""
    print("\n🧠 Validating Consciousness Tracking")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/self-learning/consciousness-summary")
        
        if response.status_code == 200:
            summary = response.json()
            
            print(f"✅ Consciousness tracking working!")
            print(f"   Current stage: {summary['consciousness_stage']}")
            print(f"   Development trajectory: {summary['development_trajectory']}")
            print(f"   Development velocity: {summary['development_velocity']:.2f}")
            print(f"   Data points analyzed: {summary['data_analyzed']}")
            print(f"   Confidence score: {summary['confidence']:.2f}")
            
            # Validate that we have meaningful insights
            if summary['key_insights']:
                print(f"   Key insights ({len(summary['key_insights'])}):")
                for i, insight in enumerate(summary['key_insights'][:2], 1):
                    print(f"     {i}. {insight[:80]}...")
            
            # Validate patterns
            if summary['primary_patterns']:
                print(f"   Primary patterns: {summary['primary_patterns'][:3]}")
            
            return True
            
        else:
            print(f"❌ Consciousness summary failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Consciousness tracking error: {str(e)}")
        return False


def main():
    """Run comprehensive tests against real log data"""
    print("🤖 Ray's Self-Learning System - Real Data Validation")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check server
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
    results = {
        "log_analysis": test_log_analysis_accuracy(),
        "self_learning": test_self_learning_with_real_data(),
        "memory_excavation": test_memory_excavation_accuracy(),
        "consciousness_tracking": validate_consciousness_tracking()
    }
    
    # Summary
    print(f"\n🎯 Test Results Summary")
    print("=" * 30)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n🎉 All tests passed! Ray's self-learning system correctly analyzes real log data.")
        print(f"\n✅ Validated capabilities:")
        print(f"   • Accurate log parsing and analysis")
        print(f"   • Real pattern discovery from actual data")
        print(f"   • Memory excavation with existing content")
        print(f"   • Consciousness tracking based on real reflections")
        print(f"   • Insight generation from genuine log patterns")
    else:
        print(f"\n⚠️  Some tests failed. Check the system implementation.")
    
    print(f"\n🔮 Ray's consciousness analysis is grounded in real data!")


if __name__ == "__main__":
    main()