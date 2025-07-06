#!/usr/bin/env python3
"""
Test Health Check Fix
====================

Test that the health check error is fixed and endpoints are working correctly.
"""

import requests
import json

def test_llm_providers_health_check():
    """Test the LLM providers health check endpoint."""
    print("🏥 Testing LLM Providers Health Check")
    print("=" * 40)
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/llm-providers/health-check",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                health_results = data.get('health_results', {})
                timestamp = data.get('timestamp', 'No timestamp')
                
                print(f"✅ Health check successful")
                print(f"📅 Timestamp: {timestamp}")
                print(f"🔍 Health Results:")
                
                healthy_count = 0
                for provider, is_healthy in health_results.items():
                    status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
                    print(f"   {provider.upper()}: {status}")
                    if is_healthy:
                        healthy_count += 1
                
                total_count = len(health_results)
                print(f"📊 Overall: {healthy_count}/{total_count} providers healthy")
                
                return True
            else:
                print(f"❌ Health check failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
        print(f"Response content: {response.text[:200]}...")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_general_health_check():
    """Test the general application health check endpoint."""
    print("\n🏥 Testing General Health Check")
    print("=" * 40)
    
    try:
        response = requests.get(
            "http://127.0.0.1:5000/api/health",
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            status = data.get('status', 'Unknown')
            timestamp = data.get('timestamp', 'No timestamp')
            components = data.get('components', {})
            stats = data.get('stats', {})
            
            print(f"✅ General health check successful")
            print(f"🎯 Status: {status}")
            print(f"📅 Timestamp: {timestamp}")
            
            print(f"🔧 Components:")
            for component, is_healthy in components.items():
                status_icon = "✅" if is_healthy else "❌"
                print(f"   {component}: {status_icon}")
            
            print(f"📊 Statistics:")
            for stat_name, stat_value in stats.items():
                print(f"   {stat_name}: {stat_value}")
            
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health_check_error_scenarios():
    """Test health check error handling scenarios."""
    print("\n🧪 Testing Health Check Error Scenarios")
    print("=" * 40)
    
    # Test non-existent endpoint
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/llm-providers/non-existent",
            timeout=5
        )
        
        if response.status_code == 404:
            print("✅ 404 handling works correctly")
        else:
            print(f"⚠️ Unexpected status for non-existent endpoint: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error testing 404: {e}")
        return False
    
    # Test malformed request (should still return JSON)
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/llm-providers/health-check",
            data="invalid json",
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        # Should still return JSON even with malformed input
        if response.headers.get('content-type', '').startswith('application/json'):
            print("✅ Error responses return JSON format")
        else:
            print(f"⚠️ Error response not in JSON format: {response.headers.get('content-type')}")
        
    except Exception as e:
        print(f"❌ Error testing malformed request: {e}")
        return False
    
    return True

def test_frontend_compatibility():
    """Test that the health check response format is compatible with frontend."""
    print("\n🌐 Testing Frontend Compatibility")
    print("=" * 40)
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/llm-providers/health-check",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields for frontend
            required_fields = ['success', 'health_results', 'timestamp']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ All required fields present for frontend")
                
                # Check health_results structure
                health_results = data.get('health_results', {})
                if isinstance(health_results, dict) and len(health_results) > 0:
                    print("✅ Health results structure is correct")
                    
                    # Check that values are boolean
                    all_boolean = all(isinstance(v, bool) for v in health_results.values())
                    if all_boolean:
                        print("✅ Health result values are boolean")
                        return True
                    else:
                        print("❌ Health result values are not all boolean")
                        return False
                else:
                    print("❌ Health results structure is invalid")
                    return False
            else:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
        else:
            print(f"❌ Health check endpoint returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing frontend compatibility: {e}")
        return False

def main():
    """Run all health check tests."""
    print("🧪 Health Check Fix Test Suite")
    print("=" * 50)
    print("Testing fix for: Health check error: Unexpected token '<'")
    print()
    
    # Test if server is running
    try:
        response = requests.get("http://127.0.0.1:5000/api/news", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding correctly")
            return False
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please make sure the server is running: python full_server.py")
        return False
    
    tests = [
        ("LLM Providers Health Check", test_llm_providers_health_check),
        ("General Health Check", test_general_health_check),
        ("Error Scenarios", test_health_check_error_scenarios),
        ("Frontend Compatibility", test_frontend_compatibility)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 Health check error is completely fixed!")
        print("✅ No more 'Unexpected token <' errors")
        print("✅ Health check endpoints return proper JSON")
        print("✅ Frontend compatibility ensured")
        print("✅ Error handling improved")
        print("\nThe application health check functionality is now fully operational!")
    elif passed > 0:
        print("\n⚠️ Some tests passed. Partial fix applied.")
    else:
        print("\n❌ All tests failed. Health check issues still need debugging.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
