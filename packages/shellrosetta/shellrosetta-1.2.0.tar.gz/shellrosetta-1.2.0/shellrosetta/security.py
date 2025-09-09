"""Security validation and command sanitization for ShellRosetta.

This module provides security validation, command sanitization,
and threat detection utilities.
"""
import re
from enum import Enum
from typing import List, Dict
from dataclasses import dataclass


class SecurityLevel(Enum):
    """Security levels for command validation."""
    PERMISSIVE = "permissive"  # Allow most commands
    MODERATE = "moderate"      # Block dangerous commands
    STRICT = "strict"          # Block potentially risky commands
    PARANOID = "paranoid"      # Block everything except basic commands


@dataclass
class SecurityViolation:
    """Represents a security violation."""
    command: str
    violation_type: str
    description: str
    severity: str


class CommandValidator:
    """Validates commands for security issues."""

    def __init__(self, security_level: SecurityLevel = SecurityLevel.MODERATE):
        self.security_level = security_level
        self.violations: List[SecurityViolation] = []

        # Define dangerous patterns based on security level
        self.dangerous_patterns = {
            SecurityLevel.PERMISSIVE: [
                r'rm\s+-rf\s+/',  # Only block rm -rf /
                r'format\s+[a-z]:',  # Block disk formatting
            ],
            SecurityLevel.MODERATE: [
                r'rm\s+-rf\s+/',  # rm -rf /
                r'format\s+[a-z]:',  # disk formatting
                r'mkfs\.',  # filesystem creation
                r'dd\s+if=.*of=/dev/',  # direct disk writes
                r'>\s*/dev/',  # redirect to device files
                r'curl\s+.*\|\s*sh',  # curl | sh
                r'wget\s+.*\|\s*sh',  # wget | sh
            ],
            SecurityLevel.STRICT: [
                r'rm\s+-rf\s+/',  # rm -rf /
                r'format\s+[a-z]:',  # disk formatting
                r'mkfs\.',  # filesystem creation
                r'dd\s+if=.*of=/dev/',  # direct disk writes
                r'>\s*/dev/',  # redirect to device files
                r'curl\s+.*\|\s*sh',  # curl | sh
                r'wget\s+.*\|\s*sh',  # wget | sh
                r'sudo\s+',  # sudo commands
                r'su\s+',  # su commands
                r'chmod\s+777',  # dangerous permissions
                r'chown\s+.*:',  # ownership changes
                r'passwd\s+',  # password changes
                r'useradd\s+',  # user creation
                r'userdel\s+',  # user deletion
            ],
            SecurityLevel.PARANOID: [
                r'rm\s+',  # any rm command
                r'mv\s+',  # any mv command
                r'cp\s+',  # any cp command
                r'sudo\s+',  # sudo commands
                r'su\s+',  # su commands
                r'chmod\s+',  # permission changes
                r'chown\s+',  # ownership changes
                r'passwd\s+',  # password changes
                r'useradd\s+',  # user creation
                r'userdel\s+',  # user deletion
                r'curl\s+',  # curl commands
                r'wget\s+',  # wget commands
                r'nc\s+',  # netcat commands
                r'telnet\s+',  # telnet commands
                r'ssh\s+',  # ssh commands
                r'scp\s+',  # scp commands
                r'rsync\s+',  # rsync commands
            ]
        }

        # Define allowed commands for paranoid mode
        self.allowed_commands = {
            'ls', 'pwd', 'cat', 'head', 'tail', 'grep', 'find',
            'which', 'whereis', 'man', 'help', 'echo', 'date',
            'whoami', 'id', 'env', 'ps', 'top', 'df', 'du'
        }

    def validate_command(self, command: str) -> List[SecurityViolation]:
        """Validate a command for security issues."""
        self.violations = []
        command_lower = command.lower().strip()

        # Check for dangerous patterns
        patterns = self.dangerous_patterns.get(self.security_level, [])
        for pattern in patterns:
            if re.search(pattern, command_lower):
                self.violations.append(SecurityViolation(
                    command=command,
                    violation_type="dangerous_pattern",
                    description=f"Command matches dangerous pattern: {pattern}",
                    severity="HIGH"
                ))

        # For paranoid mode, only allow specific commands
        if self.security_level == SecurityLevel.PARANOID:
            first_word = command_lower.split()[0] if command_lower.split() else ""
            if first_word not in self.allowed_commands:
                self.violations.append(SecurityViolation(
                    command=command,
                    violation_type="unauthorized_command",
                    description=f"Command '{first_word}' not allowed in paranoid mode",
                    severity="HIGH"
                ))

        # Check for command injection patterns
        injection_patterns = [
            r';\s*',  # command separator
            r'\|\s*',  # pipe
            r'&&\s*',  # logical AND
            r'\|\|\s*',  # logical OR
            r'`.*`',  # backticks
            r'\$\(.*\)',  # command substitution
            r'<\(.*\)',  # process substitution
        ]

        for pattern in injection_patterns:
            if re.search(pattern, command):
                self.violations.append(SecurityViolation(
                    command=command,
                    violation_type="command_injection",
                    description=f"Potential command injection: {pattern}",
                    severity="MEDIUM"
                ))

        # Check for file system access patterns
        if self.security_level in [SecurityLevel.STRICT, SecurityLevel.PARANOID]:
            fs_patterns = [
                r'/etc/',  # system config
                r'/var/',  # variable data
                r'/usr/',  # user programs
                r'/bin/',  # binaries
                r'/sbin/',  # system binaries
                r'/root/',  # root directory
            ]

            for pattern in fs_patterns:
                if re.search(pattern, command):
                    self.violations.append(SecurityViolation(
                        command=command,
                        violation_type="system_access",
                        description=f"Access to system directory: {pattern}",
                        severity="MEDIUM"
                    ))

        return self.violations

    def is_safe(self, command: str) -> bool:
        """Check if a command is safe to execute."""
        violations = self.validate_command(command)
        return len(violations) == 0

    def get_violations(self) -> List[SecurityViolation]:
        """Get the list of security violations."""
        return self.violations

    def set_security_level(self, level: SecurityLevel):
        """Set the security level."""
        self.security_level = level


def sanitize_command(command: str) -> str:
    """Sanitize a command by removing potentially dangerous characters."""
    # Remove null bytes
    command = command.replace('\x00', '')
    
    # Remove control characters except newlines and tabs
    command = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', command)
    
    # Limit command length
    if len(command) > 1000:
        command = command[:1000]
    
    return command.strip()


def validate_file_path(path: str) -> bool:
    """Validate that a file path is safe."""
    # Check for path traversal
    if '..' in path or path.startswith('/'):
        return False
    
    # Check for dangerous characters
    dangerous_chars = ['<', '>', '|', '&', ';', '`', '$', '(', ')']
    if any(char in path for char in dangerous_chars):
        return False
    
    return True


def get_security_report(
    command: str,
    security_level: SecurityLevel = SecurityLevel.MODERATE
) -> Dict[str, any]:
    """Get a comprehensive security report for a command."""
    validator = CommandValidator(security_level)
    violations = validator.validate_command(command)

    return {
        'command': command,
        'security_level': security_level.value,
        'is_safe': len(violations) == 0,
        'violation_count': len(violations),
        'violations': [
            {
                'type': v.violation_type,
                'description': v.description,
                'severity': v.severity
            }
            for v in violations
        ],
        'sanitized_command': sanitize_command(command)
    }


# Global command validator instance
command_validator = CommandValidator()