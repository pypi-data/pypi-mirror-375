"""
Security threat detection algorithms
"""

import re
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple, Optional
from .parsers import LogEntry


class ThreatEvent:
    """Represents a detected security threat"""
    
    def __init__(self, threat_type: str, severity: str, source_ip: str, 
                 description: str, timestamp: datetime, details: Dict = None):
        self.threat_type = threat_type
        self.severity = severity  # LOW, MEDIUM, HIGH, CRITICAL
        self.source_ip = source_ip
        self.description = description
        self.timestamp = timestamp
        self.details = details or {}
        self.count = 1
    
    def __str__(self):
        return f"[{self.severity}] {self.threat_type}: {self.description} from {self.source_ip}"


class SSHBruteForceDetector:
    """Detects SSH brute-force attacks"""
    
    def __init__(self, failed_threshold: int = 5, time_window: int = 300):
        self.failed_threshold = failed_threshold  # Number of failed attempts
        self.time_window = time_window  # Time window in seconds
        self.failed_attempts = defaultdict(list)  # IP -> list of timestamps
        self.patterns = {
            'ssh_failed_password': re.compile(r'Failed password for (?:invalid user )?(\w+) from ([\d\.]+) port (\d+)'),
            'ssh_failed_publickey': re.compile(r'Failed publickey for (?:invalid user )?(\w+) from ([\d\.]+) port (\d+)'),
            'ssh_invalid_user': re.compile(r'Invalid user (\w+) from ([\d\.]+) port (\d+)'),
            'ssh_connection_closed': re.compile(r'Connection closed by ([\d\.]+) port (\d+)'),
            'ssh_preauth_disconnect': re.compile(r'Disconnected from ([\d\.]+) port (\d+).*preauth'),
            'ssh_break_in_attempt': re.compile(r'POSSIBLE BREAK-IN ATTEMPT.*from ([\d\.]+)'),
        }
    
    def analyze_entry(self, entry: LogEntry) -> List[ThreatEvent]:
        """Analyze a single log entry for SSH brute-force patterns"""
        threats = []
        
        if 'ssh' not in entry.source.lower():
            return threats
        
        message = entry.message
        timestamp = entry.timestamp
        
        # Check for various SSH failure patterns
        for pattern_name, pattern in self.patterns.items():
            match = pattern.search(message)
            if match:
                if pattern_name in ['ssh_failed_password', 'ssh_failed_publickey', 'ssh_invalid_user']:
                    username = match.group(1)
                    source_ip = match.group(2)
                    port = match.group(3)
                    
                    # Track failed attempts
                    self.failed_attempts[source_ip].append(timestamp)
                    
                    # Clean old attempts outside time window
                    cutoff_time = timestamp - timedelta(seconds=self.time_window)
                    self.failed_attempts[source_ip] = [
                        t for t in self.failed_attempts[source_ip] if t > cutoff_time
                    ]
                    
                    # Check if threshold exceeded
                    attempt_count = len(self.failed_attempts[source_ip])
                    if attempt_count >= self.failed_threshold:
                        severity = self._calculate_severity(attempt_count)
                        threat = ThreatEvent(
                            threat_type="SSH_BRUTE_FORCE",
                            severity=severity,
                            source_ip=source_ip,
                            description=f"SSH brute-force attack detected: {attempt_count} failed attempts in {self.time_window}s",
                            timestamp=timestamp,
                            details={
                                'username': username,
                                'port': port,
                                'attempt_count': attempt_count,
                                'pattern': pattern_name,
                                'time_window': self.time_window
                            }
                        )
                        threats.append(threat)
                
                elif pattern_name == 'ssh_break_in_attempt':
                    source_ip = match.group(1)
                    threat = ThreatEvent(
                        threat_type="SSH_BREAK_IN_ATTEMPT",
                        severity="HIGH",
                        source_ip=source_ip,
                        description="Possible SSH break-in attempt detected",
                        timestamp=timestamp,
                        details={'pattern': pattern_name}
                    )
                    threats.append(threat)
        
        return threats
    
    def _calculate_severity(self, attempt_count: int) -> str:
        """Calculate threat severity based on attempt count"""
        if attempt_count >= 50:
            return "CRITICAL"
        elif attempt_count >= 20:
            return "HIGH"
        elif attempt_count >= 10:
            return "MEDIUM"
        else:
            return "LOW"


class RootAccessDetector:
    """Detects unauthorized root access attempts"""
    
    def __init__(self):
        self.patterns = {
            'su_failed': re.compile(r'FAILED SU \(to (\w+)\) (\w+) on (.*)'),
            'su_success': re.compile(r'Successful su for (\w+) by (\w+)'),
            'sudo_failed': re.compile(r'sudo.*authentication failure.*user=(\w+)'),
            'sudo_success': re.compile(r'sudo.*COMMAND=(.*).*user=(\w+)'),
            'root_login_failed': re.compile(r'Failed password for root from ([\d\.]+)'),
            'root_login_success': re.compile(r'Accepted (?:password|publickey) for root from ([\d\.]+)'),
            'privilege_escalation': re.compile(r'.*privilege.*escalation.*'),
            'unauthorized_root': re.compile(r'.*unauthorized.*root.*'),
        }
        self.suspicious_commands = {
            '/bin/bash', '/bin/sh', '/bin/zsh', 'passwd', 'useradd', 'usermod', 
            'userdel', 'groupadd', 'groupmod', 'groupdel', 'chmod 777', 'chown root'
        }
    
    def analyze_entry(self, entry: LogEntry) -> List[ThreatEvent]:
        """Analyze a single log entry for root access patterns"""
        threats = []
        message = entry.message
        timestamp = entry.timestamp
        
        for pattern_name, pattern in self.patterns.items():
            match = pattern.search(message)
            if match:
                if pattern_name == 'su_failed':
                    target_user = match.group(1)
                    source_user = match.group(2)
                    terminal = match.group(3)
                    
                    if target_user == 'root':
                        threat = ThreatEvent(
                            threat_type="UNAUTHORIZED_ROOT_ACCESS",
                            severity="HIGH",
                            source_ip="localhost",
                            description=f"Failed su attempt to root by user '{source_user}'",
                            timestamp=timestamp,
                            details={
                                'target_user': target_user,
                                'source_user': source_user,
                                'terminal': terminal,
                                'pattern': pattern_name
                            }
                        )
                        threats.append(threat)
                
                elif pattern_name == 'root_login_failed':
                    source_ip = match.group(1)
                    threat = ThreatEvent(
                        threat_type="ROOT_LOGIN_ATTEMPT",
                        severity="CRITICAL",
                        source_ip=source_ip,
                        description="Failed direct root login attempt",
                        timestamp=timestamp,
                        details={'pattern': pattern_name}
                    )
                    threats.append(threat)
                
                elif pattern_name == 'root_login_success':
                    source_ip = match.group(1)
                    threat = ThreatEvent(
                        threat_type="ROOT_LOGIN_SUCCESS",
                        severity="CRITICAL",
                        source_ip=source_ip,
                        description="Successful direct root login",
                        timestamp=timestamp,
                        details={'pattern': pattern_name}
                    )
                    threats.append(threat)
                
                elif pattern_name == 'sudo_success':
                    command = match.group(1)
                    user = match.group(2)
                    
                    # Check for suspicious commands
                    if any(sus_cmd in command.lower() for sus_cmd in self.suspicious_commands):
                        severity = "HIGH" if any(cmd in command for cmd in ['/bin/bash', '/bin/sh', 'passwd']) else "MEDIUM"
                        threat = ThreatEvent(
                            threat_type="SUSPICIOUS_SUDO_COMMAND",
                            severity=severity,
                            source_ip="localhost",
                            description=f"Suspicious sudo command executed by '{user}': {command}",
                            timestamp=timestamp,
                            details={
                                'command': command,
                                'user': user,
                                'pattern': pattern_name
                            }
                        )
                        threats.append(threat)
        
        return threats


class FailedLoginDetector:
    """Detects patterns of failed login attempts"""
    
    def __init__(self, threshold: int = 3, time_window: int = 600):
        self.threshold = threshold
        self.time_window = time_window
        self.failed_logins = defaultdict(list)
        self.patterns = {
            'login_failed': re.compile(r'authentication failure.*user=(\w+)'),
            'pam_failed': re.compile(r'PAM.*authentication failure.*user=(\w+)'),
            'login_incorrect': re.compile(r'LOGIN.*FAILURE.*user=(\w+)'),
        }
    
    def analyze_entry(self, entry: LogEntry) -> List[ThreatEvent]:
        """Analyze entry for failed login patterns"""
        threats = []
        message = entry.message
        timestamp = entry.timestamp
        
        for pattern_name, pattern in self.patterns.items():
            match = pattern.search(message)
            if match:
                username = match.group(1)
                
                # Track failed attempts
                self.failed_logins[username].append(timestamp)
                
                # Clean old attempts
                cutoff_time = timestamp - timedelta(seconds=self.time_window)
                self.failed_logins[username] = [
                    t for t in self.failed_logins[username] if t > cutoff_time
                ]
                
                # Check threshold
                attempt_count = len(self.failed_logins[username])
                if attempt_count >= self.threshold:
                    severity = "HIGH" if attempt_count >= 10 else "MEDIUM"
                    threat = ThreatEvent(
                        threat_type="REPEATED_LOGIN_FAILURES",
                        severity=severity,
                        source_ip="localhost",
                        description=f"Multiple login failures for user '{username}': {attempt_count} attempts",
                        timestamp=timestamp,
                        details={
                            'username': username,
                            'attempt_count': attempt_count,
                            'time_window': self.time_window
                        }
                    )
                    threats.append(threat)
        
        return threats
