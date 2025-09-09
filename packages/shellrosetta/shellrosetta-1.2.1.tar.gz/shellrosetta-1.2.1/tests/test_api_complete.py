#!/usr/bin/env python3
"""
Complete API testing
"""

import sys
import os
import time
import threading
import requests
from multiprocessing import Process
# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def start_test_server():
    """Start API server for testing"""
    from shellrosetta.api import run_api_server
    run_api_server(host="127.0.0.1", port=5001, debug=False)

def test_api_basic_functionality():
    """Test basic API functionality"""
    
    base_url = "http://127.0.0.1:5001"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health endpoint working")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False
    
    # Test translation endpoint
    try:
        response = requests.post(
            f"{base_url}/api/translate",
            json={"command": "ls -la", "direction": "lnx2ps"},
            timeout=5
        )
        assert response.status_code == 200
        data = response.json()
        assert "translation" in data
        assert "Get-ChildItem" in data["translation"]
        print("✅ Translation endpoint working")
    except Exception as e:
        print(f"❌ Translation endpoint failed: {e}")
        return False
    
    # Test validation endpoint
    try:
        response = requests.post(
            f"{base_url}/api/validate",
            json={"command": "ls -la"},
            timeout=5
        )
        assert response.status_code == 200
        data = response.json()
        assert "is_valid" in data
        print("✅ Validation endpoint working")
    except Exception as e:
        print(f"❌ Validation endpoint failed: {e}")
        return False
    
    return True

def test_api_security():
    """Test API security features"""
    
    base_url = "http://127.0.0.1:5001"
    
    # Test security headers
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        headers = response.headers
        
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection'
        ]
        
        for header in security_headers:
            assert header in headers, f"Missing security header: {header}"
        
        print("✅ Security headers present")
    except Exception as e:
        print(f"❌ Security headers test failed: {e}")
        return False
    
    # Test dangerous command blocking
    try:
        response = requests.post(
            f"{base_url}/api/translate",
            json={"command": "ls; rm -rf /", "direction": "lnx2ps"},
            timeout=5
        )
        
        # Should either block with 400 or return safe translation
        if response.status_code == 400:
            print("✅ Dangerous command blocked by API")
        else:
            data = response.json()
            if "SECURITY ERROR" in data.get("translation", ""):
                print("✅ Dangerous command handled safely")
            else:
                print("⚠️  Dangerous command processed (check security settings)")
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🌐 Complete API Testing")
    print("=" * 40)
    
    print("Starting test server...")
    
    # Start server in separate process
    server_process = Process(target=start_test_server)
    server_process.start()
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Run tests
        basic_result = test_api_basic_functionality()
        security_result = test_api_security()
        
        if basic_result and security_result:
            print("\n🎉 All API tests passed!")
        else:
            print("\n❌ Some API tests failed!")
            
    except Exception as e:
        print(f"❌ API testing failed: {e}")
    finally:
        # Clean up
        server_process.terminate()
        server_process.join()
        print("Test server stopped")