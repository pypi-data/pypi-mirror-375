"""
Command-line interface for LogHero
"""

import click
import os
import sys
from datetime import datetime
from colorama import init, Fore, Style
from tabulate import tabulate
from .analyzer import LogAnalyzer

# Initialize colorama for cross-platform colored output
init(autoreset=True)


def print_banner():
    """Print LogHero banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                          LogHero v1.0.0                     ║
║                  System Log Security Analyzer               ║
║              Detecting suspicious activities...             ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    click.echo(banner)


def format_threat_severity(severity):
    """Format threat severity with colors"""
    colors = {
        'CRITICAL': Fore.RED + Style.BRIGHT,
        'HIGH': Fore.RED,
        'MEDIUM': Fore.YELLOW,
        'LOW': Fore.GREEN
    }
    return f"{colors.get(severity, '')}{severity}{Style.RESET_ALL}"


def format_threat_type(threat_type):
    """Format threat type with colors"""
    return f"{Fore.MAGENTA}{threat_type}{Style.RESET_ALL}"


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """LogHero - System Log Security Analyzer
    
    Analyze system logs to detect suspicious activities like SSH brute-force
    attacks and unauthorized root access attempts.
    """
    pass


@cli.command()
@click.argument('log_file', type=click.Path(exists=True, readable=True))
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'csv']), 
              default='table', help='Output format')
@click.option('--severity', '-s', type=click.Choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
              help='Filter by minimum severity level')
@click.option('--threat-type', '-t', help='Filter by threat type')
@click.option('--limit', '-l', type=int, default=50, help='Limit number of results')
@click.option('--quiet', '-q', is_flag=True, help='Suppress banner and extra output')
@click.option('--save-report', type=click.Path(), help='Save detailed report to file')
def scan(log_file, output, severity, threat_type, limit, quiet, save_report):
    """Scan a log file for security threats
    
    Examples:
        loghero scan /var/log/auth.log
        loghero scan /var/log/secure --severity HIGH
        loghero scan system.log --output json --save-report report.json
    """
    if not quiet:
        print_banner()
        click.echo(f"{Fore.BLUE}📁 Analyzing log file: {log_file}{Style.RESET_ALL}")
        click.echo()
    
    # Initialize analyzer
    analyzer = LogAnalyzer()
    
    try:
        # Analyze the log file
        with click.progressbar(length=100, label='Scanning log file') as bar:
            result = analyzer.analyze_file(log_file)
            bar.update(100)
        
        if 'error' in result:
            click.echo(f"{Fore.RED}❌ Error: {result['error']}{Style.RESET_ALL}", err=True)
            sys.exit(1)
        
        threats = result['threats']
        stats = result['stats']
        
        # Apply filters
        if severity:
            severity_order = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2, 'CRITICAL': 3}
            min_level = severity_order[severity]
            threats = [t for t in threats if severity_order.get(t.severity, 0) >= min_level]
        
        if threat_type:
            threats = [t for t in threats if threat_type.upper() in t.threat_type]
        
        # Limit results
        threats = threats[:limit]
        
        if not quiet:
            # Display summary statistics
            click.echo(f"{Fore.GREEN}📊 Analysis Summary:{Style.RESET_ALL}")
            click.echo(f"   • Total log entries processed: {stats['total_entries_processed']:,}")
            click.echo(f"   • Total threats found: {stats['total_threats_found']}")
            click.echo(f"   • Unique source IPs: {stats['unique_source_ips']}")
            click.echo()
        
        if threats:
            if output == 'table':
                display_threats_table(threats, quiet)
            elif output == 'json':
                display_threats_json(threats)
            elif output == 'csv':
                display_threats_csv(threats)
            
            if not quiet:
                # Display top threatening IPs
                top_ips = result.get('top_threat_ips', [])[:5]
                if top_ips:
                    click.echo(f"\n{Fore.RED}🎯 Top Threatening IPs:{Style.RESET_ALL}")
                    ip_table = []
                    for ip_info in top_ips:
                        ip_table.append([
                            ip_info['ip'],
                            ip_info['threat_count'],
                            ip_info['severity_score'],
                            ', '.join(ip_info['threat_types'][:2])
                        ])
                    
                    click.echo(tabulate(ip_table, 
                                      headers=['IP Address', 'Threats', 'Score', 'Types'],
                                      tablefmt='grid'))
                
                # Display recommendations
                recommendations = result.get('recommendations', [])
                if recommendations:
                    click.echo(f"\n{Fore.YELLOW}💡 Security Recommendations:{Style.RESET_ALL}")
                    for i, rec in enumerate(recommendations[:5], 1):
                        click.echo(f"   {i}. {rec}")
        else:
            if not quiet:
                click.echo(f"{Fore.GREEN}✅ No security threats detected in the log file.{Style.RESET_ALL}")
        
        # Save detailed report if requested
        if save_report:
            save_detailed_report(result, save_report)
            if not quiet:
                click.echo(f"\n{Fore.BLUE}💾 Detailed report saved to: {save_report}{Style.RESET_ALL}")
    
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}⚠️  Analysis interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}❌ Unexpected error: {str(e)}{Style.RESET_ALL}", err=True)
        sys.exit(1)


def display_threats_table(threats, quiet=False):
    """Display threats in table format"""
    if not quiet:
        click.echo(f"{Fore.RED}🚨 Security Threats Detected:{Style.RESET_ALL}")
    
    table_data = []
    for threat in threats:
        table_data.append([
            threat.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            format_threat_severity(threat.severity),
            format_threat_type(threat.threat_type),
            threat.source_ip,
            threat.description[:60] + ('...' if len(threat.description) > 60 else ''),
            str(threat.count) if threat.count > 1 else '1'
        ])
    
    click.echo(tabulate(table_data,
                       headers=['Timestamp', 'Severity', 'Type', 'Source IP', 'Description', 'Count'],
                       tablefmt='grid'))


def display_threats_json(threats):
    """Display threats in JSON format"""
    import json
    
    threat_data = []
    for threat in threats:
        threat_data.append({
            'timestamp': threat.timestamp.isoformat(),
            'severity': threat.severity,
            'threat_type': threat.threat_type,
            'source_ip': threat.source_ip,
            'description': threat.description,
            'count': threat.count,
            'details': threat.details
        })
    
    click.echo(json.dumps(threat_data, indent=2))


def display_threats_csv(threats):
    """Display threats in CSV format"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Timestamp', 'Severity', 'Threat Type', 'Source IP', 'Description', 'Count'])
    
    # Write data
    for threat in threats:
        writer.writerow([
            threat.timestamp.isoformat(),
            threat.severity,
            threat.threat_type,
            threat.source_ip,
            threat.description,
            threat.count
        ])
    
    click.echo(output.getvalue())


def save_detailed_report(result, filename):
    """Save detailed analysis report"""
    import json
    
    # Convert threats to serializable format
    serializable_threats = []
    for threat in result['threats']:
        serializable_threats.append({
            'timestamp': threat.timestamp.isoformat(),
            'severity': threat.severity,
            'threat_type': threat.threat_type,
            'source_ip': threat.source_ip,
            'description': threat.description,
            'count': threat.count,
            'details': threat.details
        })
    
    report_data = {
        'analysis_timestamp': datetime.now().isoformat(),
        'loghero_version': '1.0.0',
        'threats': serializable_threats,
        'statistics': result['stats'],
        'top_threat_ips': result.get('top_threat_ips', []),
        'recommendations': result.get('recommendations', [])
    }
    
    with open(filename, 'w') as f:
        json.dump(report_data, f, indent=2)


@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--pattern', '-p', default='*.log', help='File pattern to match')
@click.option('--recursive', '-r', is_flag=True, help='Search recursively')
def batch(directory, pattern, recursive):
    """Batch analyze multiple log files in a directory
    
    Examples:
        loghero batch /var/log
        loghero batch /var/log --pattern "auth*" --recursive
    """
    print_banner()
    
    import glob
    
    # Find log files
    if recursive:
        pattern_path = os.path.join(directory, '**', pattern)
        log_files = glob.glob(pattern_path, recursive=True)
    else:
        pattern_path = os.path.join(directory, pattern)
        log_files = glob.glob(pattern_path)
    
    if not log_files:
        click.echo(f"{Fore.YELLOW}⚠️  No log files found matching pattern: {pattern}{Style.RESET_ALL}")
        return
    
    click.echo(f"{Fore.BLUE}📁 Found {len(log_files)} log files to analyze{Style.RESET_ALL}")
    
    analyzer = LogAnalyzer()
    all_threats = []
    
    for log_file in log_files:
        click.echo(f"\n{Fore.CYAN}Analyzing: {log_file}{Style.RESET_ALL}")
        
        try:
            result = analyzer.analyze_file(log_file)
            if 'error' not in result:
                threats = result['threats']
                for threat in threats:
                    threat.details['source_file'] = log_file
                all_threats.extend(threats)
                click.echo(f"   Found {len(threats)} threats")
            else:
                click.echo(f"   {Fore.RED}Error: {result['error']}{Style.RESET_ALL}")
        except Exception as e:
            click.echo(f"   {Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
    
    if all_threats:
        click.echo(f"\n{Fore.GREEN}📊 Batch Analysis Complete:{Style.RESET_ALL}")
        click.echo(f"   • Total threats found: {len(all_threats)}")
        
        # Sort by severity and display top threats
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        all_threats.sort(key=lambda t: (severity_order.get(t.severity, 4), t.timestamp), reverse=True)
        
        display_threats_table(all_threats[:20], quiet=True)
    else:
        click.echo(f"\n{Fore.GREEN}✅ No security threats detected in any log files.{Style.RESET_ALL}")


def main():
    """Main entry point"""
    cli()


if __name__ == '__main__':
    main()
