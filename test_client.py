#!/usr/bin/env python3
"""
Test client for the Local AI Agent API
Tests file creation functionality
"""

import requests
import json
import sys
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test API health"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_agent_health():
    """Test agent service health"""
    try:
        response = requests.get(f"{BASE_URL}/api/agent/health")
        print(f"✅ Agent health check: {response.status_code}")
        result = response.json()
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Tools available: {result.get('tools_available', 0)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Agent health check failed: {e}")
        return False

def test_available_tools():
    """Test getting available tools"""
    try:
        response = requests.get(f"{BASE_URL}/api/agent/tools")
        print(f"✅ Available tools: {response.status_code}")
        result = response.json()
        
        print(f"   Total tools: {result.get('count', 0)}")
        print(f"   Enabled tools: {result.get('enabled_count', 0)}")
        
        for tool in result.get('tools', []):
            print(f"   - {tool['name']}: {tool['description'][:50]}...")
            if 'allowed_paths_count' in tool:
                print(f"     Allowed paths: {tool['allowed_paths_count']}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Available tools test failed: {e}")
        return False

def test_file_write():
    """Test file writing functionality"""
    try:
        # Test data
        file_path = "/Users/mac/Desktop/jongho_project/jongho_service/local_ai_agent/hi.txt"
        content = "hello world"
        
        payload = {
            "operation": "write",
            "path": file_path,
            "content": content,
            "encoding": "utf-8"
        }
        
        print(f"🔄 Testing file write to: {file_path}")
        response = requests.post(f"{BASE_URL}/api/agent/file", json=payload)
        
        print(f"   Status code: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200 and result.get('success', False):
            print(f"✅ File write successful!")
            print(f"   Path: {result['result'].get('path', 'unknown')}")
            print(f"   Size: {result['result'].get('size', 0)} bytes")
            return True
        else:
            print(f"❌ File write failed:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ File write test failed: {e}")
        return False

def test_agent_chat():
    """Test agent chat with file creation request"""
    try:
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": "/Users/mac/Desktop/jongho_project/jongho_service/local_ai_agent/hi.txt파일에 hello world라는 스트링 적어서 저장해"
                }
            ],
            "session_id": "test-session-" + str(int(time.time())),
            "max_iterations": 3
        }
        
        print(f"🔄 Testing agent chat with file creation request...")
        response = requests.post(f"{BASE_URL}/api/agent/chat", json=payload)
        
        print(f"   Status code: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            print(f"✅ Agent chat successful!")
            print(f"   Response: {result.get('response', 'No response')}")
            print(f"   Tool calls made: {len(result.get('tool_calls', []))}")
            
            for i, tool_call in enumerate(result.get('tool_calls', [])):
                print(f"   Tool call {i+1}: {tool_call['tool']}")
                print(f"     Success: {tool_call['result']['success']}")
                if not tool_call['result']['success']:
                    print(f"     Error: {tool_call['result']['error']}")
            
            return True
        else:
            print(f"❌ Agent chat failed:")
            print(f"   Error: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Agent chat test failed: {e}")
        return False

def test_file_read():
    """Test reading the created file"""
    try:
        file_path = "/Users/mac/Desktop/jongho_project/jongho_service/local_ai_agent/hi.txt"
        
        payload = {
            "operation": "read",
            "path": file_path,
            "encoding": "utf-8"
        }
        
        print(f"🔄 Testing file read from: {file_path}")
        response = requests.post(f"{BASE_URL}/api/agent/file", json=payload)
        
        print(f"   Status code: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200 and result.get('success', False):
            print(f"✅ File read successful!")
            content = result['result'].get('content', '')
            print(f"   Content: '{content}'")
            print(f"   Size: {result['result'].get('size', 0)} bytes")
            return True
        else:
            print(f"❌ File read failed:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ File read test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Local AI Agent API Test Suite")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Agent Health Check", test_agent_health), 
        ("Available Tools", test_available_tools),
        ("Direct File Write", test_file_write),
        ("Agent Chat (File Creation)", test_agent_chat),
        ("File Read Verification", test_file_read),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the logs for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
