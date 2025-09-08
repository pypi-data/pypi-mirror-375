"""
Log parsing utilities for different operating systems
"""

import re
import os
from datetime import datetime
from typing import List, Dict, Optional, Iterator
from dateutil import parser as date_parser


class LogEntry:
    """Represents a single log entry"""
    
    def __init__(self, timestamp: datetime, message: str, source: str = "", level: str = ""):
        self.timestamp = timestamp
        self.message = message
        self.source = source
        self.level = level
        self.raw_line = ""
    
    def __str__(self):
        return f"[{self.timestamp}] {self.source}: {self.message}"


class LogParser:
    """Base log parser class"""
    
    def __init__(self):
        self.patterns = {
            'linux_auth': re.compile(r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+):\s+(.*)$'),
            'linux_syslog': re.compile(r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+)\[(\d+)\]:\s+(.*)$'),
            'macos_system': re.compile(r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})\s+(\S+)\s+(\S+)\[(\d+)\]:\s+(.*)$'),
            'windows_security': re.compile(r'^(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M)\s+(.*)$')
        }
    
    def detect_log_format(self, file_path: str) -> str:
        """Detect the log format based on file path and content"""
        file_name = os.path.basename(file_path).lower()
        
        # Check by filename
        if 'auth.log' in file_name or 'secure' in file_name:
            return 'linux_auth'
        elif 'system.log' in file_name and 'darwin' in os.uname().sysname.lower():
            return 'macos_system'
        elif 'security.evtx' in file_name or 'application.evtx' in file_name:
            return 'windows_security'
        
        # Try to detect by content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                sample_lines = [f.readline().strip() for _ in range(5)]
            
            for line in sample_lines:
                if not line:
                    continue
                    
                for format_name, pattern in self.patterns.items():
                    if pattern.match(line):
                        return format_name
        except Exception:
            pass
        
        return 'linux_auth'  # Default fallback
    
    def parse_timestamp(self, timestamp_str: str, format_type: str) -> Optional[datetime]:
        """Parse timestamp string based on format type"""
        try:
            if format_type == 'linux_auth':
                # Add current year for syslog format
                current_year = datetime.now().year
                timestamp_str = f"{current_year} {timestamp_str}"
                return datetime.strptime(timestamp_str, "%Y %b %d %H:%M:%S")
            elif format_type == 'macos_system':
                return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
            elif format_type == 'windows_security':
                return date_parser.parse(timestamp_str)
            else:
                return date_parser.parse(timestamp_str)
        except Exception:
            return datetime.now()
    
    def parse_line(self, line: str, format_type: str) -> Optional[LogEntry]:
        """Parse a single log line"""
        line = line.strip()
        if not line:
            return None
        
        pattern = self.patterns.get(format_type)
        if not pattern:
            return None
        
        match = pattern.match(line)
        if not match:
            return None
        
        groups = match.groups()
        
        if format_type == 'linux_auth':
            timestamp_str, hostname, service, message = groups
            timestamp = self.parse_timestamp(timestamp_str, format_type)
            entry = LogEntry(timestamp, message, service)
        elif format_type == 'linux_syslog':
            timestamp_str, hostname, service, pid, message = groups
            timestamp = self.parse_timestamp(timestamp_str, format_type)
            entry = LogEntry(timestamp, message, f"{service}[{pid}]")
        elif format_type == 'macos_system':
            timestamp_str, hostname, service, pid, message = groups
            timestamp = self.parse_timestamp(timestamp_str, format_type)
            entry = LogEntry(timestamp, message, f"{service}[{pid}]")
        elif format_type == 'windows_security':
            timestamp_str, message = groups
            timestamp = self.parse_timestamp(timestamp_str, format_type)
            entry = LogEntry(timestamp, message, "Security")
        else:
            return None
        
        entry.raw_line = line
        return entry
    
    def parse_file(self, file_path: str) -> Iterator[LogEntry]:
        """Parse entire log file"""
        format_type = self.detect_log_format(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    entry = self.parse_line(line, format_type)
                    if entry:
                        yield entry
        except Exception as e:
            raise Exception(f"Error parsing file {file_path}: {str(e)}")
