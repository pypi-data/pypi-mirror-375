#!/usr/bin/env python3
"""
Test that all enhanced modules can be imported correctly
"""

def test_core_imports():
    """Test core module imports"""
    try:
        from shellrosetta.core import lnx2ps, ps2lnx, get_translation_stats
        print("✅ Core module imports successful")
        return True
    except ImportError as e:
        print(f"❌ Core module import failed: {e}")
        return False

def test_security_imports():
    """Test security module imports"""
    try:
        from shellrosetta.security import CommandValidator, SecurityLevel
        print("✅ Security module imports successful")
        return True
    except ImportError as e:
        print(f"❌ Security module import failed: {e}")
        return False

def test_performance_imports():
    """Test performance module imports"""
    try:
        from shellrosetta.performance import cached, get_memory_cache
        print("✅ Performance module imports successful")
        return True
    except ImportError as e:
        print(f"❌ Performance module import failed: {e}")
        return False

def test_logging_imports():
    """Test logging module imports"""
    try:
        from shellrosetta.logging_config import get_logger, RequestContext
        print("✅ Logging module imports successful")
        return True
    except ImportError as e:
        print(f"❌ Logging module import failed: {e}")
        return False

def test_api_imports():
    """Test API module imports"""
    try:
        from shellrosetta.api import run_api_server
        print("✅ API module imports successful")
        return True
    except ImportError as e:
        print(f"❌ API module import failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Module Imports")
    print("=" * 40)
    
    tests = [
        test_core_imports,
        test_security_imports,
        test_performance_imports,
        test_logging_imports,
        test_api_imports
    ]
    
    results = [test() for test in tests]
    
    if all(results):
        print("\n🎉 All imports successful!")
    else:
        print("\n❌ Some imports failed!")
        print("Check the error messages above.")