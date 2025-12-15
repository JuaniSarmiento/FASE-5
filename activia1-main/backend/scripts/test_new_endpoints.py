"""
Script de testing rápido para validar endpoints de eventos y trazabilidad

USO:
    python backend/scripts/test_new_endpoints.py
"""
import sys
from pathlib import Path

# Agregar backend al path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

import requests
import json
from datetime import datetime

from backend.core.constants import utc_now

BASE_URL = "http://localhost:8000/api/v1"


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_response(response):
    """Print formatted response"""
    print(f"\nStatus: {response.status_code}")
    if response.status_code < 400:
        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except (json.JSONDecodeError, ValueError):
            print(response.text)
    else:
        print(f"❌ ERROR: {response.text}")


def test_sessions():
    """Test sessions endpoint"""
    print_section("TEST 1: GET /sessions?student_id=student_001")
    
    response = requests.get(f"{BASE_URL}/sessions", params={"student_id": "student_001"})
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        sessions = data.get("data", [])
        print(f"\n✅ Found {len(sessions)} sessions")
        
        if sessions:
            return sessions[0]["id"]
    
    return None


def test_events(session_id):
    """Test events endpoints"""
    if not session_id:
        print("\n⚠️  Skipping events test - no session available")
        return
    
    print_section(f"TEST 2: GET /events?session_id={session_id}")
    
    response = requests.get(f"{BASE_URL}/events", params={"session_id": session_id})
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        events = data.get("data", [])
        print(f"\n✅ Found {len(events)} events")


def test_create_event(session_id):
    """Test create event endpoint"""
    if not session_id:
        print("\n⚠️  Skipping create event test - no session available")
        return
    
    print_section(f"TEST 3: POST /events")
    
    event_data = {
        "session_id": session_id,
        "event_type": "test_event_created",
        "event_data": {
            "test": True,
            "timestamp": utc_now().isoformat(),
            "message": "This is a test event"
        },
        "description": "Test event created by test script",
        "severity": "info"
    }
    
    response = requests.post(f"{BASE_URL}/events", json=event_data)
    print_response(response)
    
    if response.status_code == 201:
        print("\n✅ Event created successfully")


def test_analyze_risks(session_id):
    """Test risk analysis endpoint"""
    if not session_id:
        print("\n⚠️  Skipping risk analysis test - no session available")
        return
    
    print_section(f"TEST 4: POST /risks/analyze-session/{session_id}")
    
    response = requests.post(f"{BASE_URL}/risks/analyze-session/{session_id}")
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        risks = data.get("data", [])
        print(f"\n✅ Detected {len(risks)} risks")
        
        if risks:
            print("\n📊 Risk Summary:")
            for risk in risks:
                print(f"   - {risk['risk_level']}: {risk['description'][:60]}...")


def test_traceability(session_id):
    """Test traceability endpoint"""
    if not session_id:
        print("\n⚠️  Skipping traceability test - no session available")
        return
    
    print_section(f"TEST 5: GET /traceability/session/{session_id}")
    
    response = requests.get(f"{BASE_URL}/traceability/session/{session_id}")
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        trace_data = data.get("data", {})
        summary = trace_data.get("summary", {})
        
        print("\n✅ Traceability graph retrieved successfully")
        print(f"\n📊 Summary:")
        print(f"   - Total Events: {summary.get('total_events', 0)}")
        print(f"   - Total Traces: {summary.get('total_traces', 0)}")
        print(f"   - Total Risks: {summary.get('total_risks', 0)}")
        print(f"   - Total Evaluations: {summary.get('total_evaluations', 0)}")
        print(f"   - Avg AI Involvement: {summary.get('avg_ai_involvement', 0):.2%}")


def test_evaluation(session_id):
    """Test evaluation endpoint"""
    if not session_id:
        print("\n⚠️  Skipping evaluation test - no session available")
        return
    
    print_section(f"TEST 6: POST /evaluations/{session_id}/generate")
    
    response = requests.post(f"{BASE_URL}/evaluations/{session_id}/generate")
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        eval_data = data.get("data", {})
        
        print("\n✅ Evaluation generated successfully")
        print(f"\n📊 Results:")
        print(f"   - Overall Score: {eval_data.get('overall_score', 0):.1f}/10")
        print(f"   - Competency Level: {eval_data.get('overall_competency_level', 'N/A')}")
        print(f"   - AI Dependency: {eval_data.get('ai_dependency_score', 0):.2%}")


def main():
    """Run all tests"""
    print("\n🚀 TESTING NEW ENDPOINTS - AI-Native MVP")
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Get sessions
        session_id = test_sessions()
        
        if not session_id:
            print("\n⚠️  WARNING: No sessions found. Run seed_dev.py first:")
            print("   python -m backend.scripts.seed_dev")
            return
        
        # Test 2: Get events
        test_events(session_id)
        
        # Test 3: Create event
        test_create_event(session_id)
        
        # Test 4: Analyze risks
        test_analyze_risks(session_id)
        
        # Test 5: Get traceability
        test_traceability(session_id)
        
        # Test 6: Generate evaluation (may take time due to LLM)
        print("\n⚠️  Note: Evaluation generation may take 30-60 seconds due to LLM processing...")
        test_evaluation(session_id)
        
        print_section("✅ ALL TESTS COMPLETED")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend")
        print("   Make sure the backend is running:")
        print("   uvicorn backend.api.main:app --reload --port 8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
