"""
Main log analysis engine
"""

from typing import List, Dict, Set
from collections import defaultdict
from .parsers import LogParser, LogEntry
from .detectors import SSHBruteForceDetector, RootAccessDetector, FailedLoginDetector, ThreatEvent


class LogAnalyzer:
    """Main log analysis engine"""
    
    def __init__(self):
        self.parser = LogParser()
        self.detectors = [
            SSHBruteForceDetector(),
            RootAccessDetector(),
            FailedLoginDetector()
        ]
        self.threats = []
        self.stats = {
            'total_entries': 0,
            'threats_found': 0,
            'unique_ips': set(),
            'threat_types': defaultdict(int)
        }
    
    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a log file and return results"""
        self.threats = []
        self.stats = {
            'total_entries': 0,
            'threats_found': 0,
            'unique_ips': set(),
            'threat_types': defaultdict(int)
        }
        
        try:
            # Parse log entries
            for entry in self.parser.parse_file(file_path):
                self.stats['total_entries'] += 1
                
                # Run all detectors on each entry
                for detector in self.detectors:
                    detected_threats = detector.analyze_entry(entry)
                    for threat in detected_threats:
                        self.threats.append(threat)
                        self.stats['unique_ips'].add(threat.source_ip)
                        self.stats['threat_types'][threat.threat_type] += 1
            
            self.stats['threats_found'] = len(self.threats)
            
            # Consolidate similar threats
            self._consolidate_threats()
            
            return self._generate_report()
            
        except Exception as e:
            return {
                'error': str(e),
                'threats': [],
                'stats': self.stats
            }
    
    def _consolidate_threats(self):
        """Consolidate similar threats to reduce noise"""
        consolidated = {}
        
        for threat in self.threats:
            # Create a key for grouping similar threats
            key = (threat.threat_type, threat.source_ip, threat.severity)
            
            if key in consolidated:
                consolidated[key].count += 1
                # Update timestamp to latest
                if threat.timestamp > consolidated[key].timestamp:
                    consolidated[key].timestamp = threat.timestamp
            else:
                consolidated[key] = threat
        
        self.threats = list(consolidated.values())
    
    def _generate_report(self) -> Dict:
        """Generate analysis report"""
        # Sort threats by severity and timestamp
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_threats = sorted(
            self.threats,
            key=lambda t: (severity_order.get(t.severity, 4), t.timestamp),
            reverse=True
        )
        
        # Generate summary statistics
        severity_counts = defaultdict(int)
        for threat in self.threats:
            severity_counts[threat.severity] += 1
        
        return {
            'file_analyzed': True,
            'threats': sorted_threats,
            'stats': {
                'total_entries_processed': self.stats['total_entries'],
                'total_threats_found': self.stats['threats_found'],
                'unique_source_ips': len(self.stats['unique_ips']),
                'threat_breakdown': dict(self.stats['threat_types']),
                'severity_breakdown': dict(severity_counts)
            },
            'top_threat_ips': self._get_top_threat_ips(),
            'recommendations': self._generate_recommendations()
        }
    
    def _get_top_threat_ips(self, limit: int = 10) -> List[Dict]:
        """Get top threatening IP addresses"""
        ip_threats = defaultdict(list)
        
        for threat in self.threats:
            if threat.source_ip != 'localhost':
                ip_threats[threat.source_ip].append(threat)
        
        # Sort by number of threats and severity
        top_ips = []
        for ip, threats in ip_threats.items():
            severity_score = sum(
                {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}.get(t.severity, 0)
                for t in threats
            )
            top_ips.append({
                'ip': ip,
                'threat_count': len(threats),
                'severity_score': severity_score,
                'threat_types': list(set(t.threat_type for t in threats))
            })
        
        return sorted(top_ips, key=lambda x: (x['severity_score'], x['threat_count']), reverse=True)[:limit]
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on findings"""
        recommendations = []
        
        # Check for SSH brute force
        ssh_threats = [t for t in self.threats if 'SSH' in t.threat_type]
        if ssh_threats:
            recommendations.extend([
                "Consider implementing fail2ban to automatically block IPs after failed SSH attempts",
                "Use SSH key authentication instead of password authentication",
                "Change SSH port from default 22 to a non-standard port",
                "Implement SSH rate limiting"
            ])
        
        # Check for root access attempts
        root_threats = [t for t in self.threats if 'ROOT' in t.threat_type]
        if root_threats:
            recommendations.extend([
                "Disable direct root login via SSH",
                "Use sudo instead of su for privilege escalation",
                "Implement proper user access controls and principle of least privilege",
                "Monitor and audit all root access attempts"
            ])
        
        # Check for high severity threats
        critical_threats = [t for t in self.threats if t.severity == 'CRITICAL']
        if critical_threats:
            recommendations.append("Immediate action required: Critical security threats detected")
        
        # General recommendations
        if self.threats:
            recommendations.extend([
                "Implement centralized logging and monitoring",
                "Set up real-time alerts for security events",
                "Regularly review and analyze system logs",
                "Keep systems updated with latest security patches"
            ])
        
        return recommendations[:10]  # Limit to top 10 recommendations
