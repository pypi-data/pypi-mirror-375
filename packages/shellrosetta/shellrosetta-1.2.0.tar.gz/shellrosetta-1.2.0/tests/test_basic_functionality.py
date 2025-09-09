#!/usr/bin/env python3
"""
Test basic ShellRosetta functionality with enhancements
"""

import sys
import os
# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_basic_translation():
    """Test basic translation still works"""
    from shellrosetta.core import lnx2ps, ps2lnx
    
    # Test Linux to PowerShell
    result = lnx2ps("ls -la")
    assert "Get-ChildItem" in result
    print("✅ Basic lnx2ps translation working")
    
    # Test PowerShell to Linux
    result = ps2lnx("Get-ChildItem -Force")
    assert "ls" in result
    print("✅ Basic ps2lnx translation working")
    
    return True

def test_security_integration():
    """Test security integration doesn't break normal operation"""
    from shellrosetta.core import lnx2ps
    
    # Safe command should work
    result = lnx2ps("ls -la")
    assert not result.startswith("# SECURITY ERROR")
    print("✅ Security integration allows safe commands")
    
    # Dangerous command should be blocked
    result = lnx2ps("ls; rm -rf /")
    assert "SECURITY ERROR" in result or "No translation" in result
    print("✅ Security integration blocks dangerous commands")
    
    return True

def test_performance_features():
    """Test performance features"""
    from shellrosetta.core import get_translation_stats, clear_translation_cache
    
    # Test stats function
    stats = get_translation_stats()
    assert isinstance(stats, dict)
    print("✅ Translation stats working")
    
    # Test cache clearing
    result = clear_translation_cache()
    assert result is True
    print("✅ Cache clearing working")
    
    return True

def test_enhanced_api():
    """Test enhanced API functions"""
    from shellrosetta.core import validate_command_security, get_translation_with_metadata
    
    # Test security validation
    validation = validate_command_security("ls -la")
    assert isinstance(validation, dict)
    assert "is_valid" in validation
    print("✅ Command security validation working")
    
    # Test metadata function
    metadata = get_translation_with_metadata("ls -la", "lnx2ps")
    assert isinstance(metadata, dict)
    assert "confidence" in metadata
    print("✅ Translation with metadata working")
    
    return True

if __name__ == "__main__":
    print("🧪 Testing Basic Functionality with Enhancements")
    print("=" * 50)
    
    tests = [
        test_basic_translation,
        test_security_integration,
        test_performance_features,
        test_enhanced_api
    ]
    
    try:
        results = [test() for test in tests]
        
        if all(results):
            print("\n🎉 All basic functionality tests passed!")
        else:
            print("\n❌ Some basic functionality tests failed!")
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()