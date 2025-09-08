# LogHero 🦸‍♂️

**System Log Security Analyzer**

*Developed by [Ahmet KAHRAMAN (AhmetXHero)](https://ahmetxhero.web.app/) - Mobile Developer & Cyber Security Expert*

LogHero is a powerful command-line tool designed to analyze system log files and detect suspicious security activities. It specializes in identifying SSH brute-force attacks, unauthorized root access attempts, and other security threats across Linux, Windows, and macOS systems.

## 🎯 Features

- **SSH Brute-Force Detection**: Identifies repeated failed SSH login attempts from the same IP
- **Root Access Monitoring**: Detects unauthorized attempts to gain root privileges
- **Multi-OS Support**: Works with Linux, Windows, and macOS log formats
- **Real-time Analysis**: Fast log parsing and threat detection
- **Detailed Reporting**: Comprehensive security reports with recommendations
- **Flexible Output**: Table, JSON, and CSV output formats
- **Batch Processing**: Analyze multiple log files at once

## 🚀 Installation

### From PyPI (Recommended)
```bash
pip install AhmetX-LogHero
```

### From Source
```bash
git clone https://github.com/ahmetxhero/AhmetX-LogHero.git
cd loghero
pip install -e .
```

## 📋 Requirements

- Python 3.7+
- Dependencies: `click`, `colorama`, `python-dateutil`, `tabulate`

## 🛠 Usage

### Basic Usage
```bash
# Analyze a single log file
loghero scan /var/log/auth.log

# Analyze with specific severity filter
loghero scan /var/log/secure --severity HIGH

# Output in JSON format
loghero scan /var/log/auth.log --output json

# Save detailed report
loghero scan /var/log/auth.log --save-report security_report.json
```

### Batch Analysis
```bash
# Analyze all log files in a directory
loghero batch /var/log

# Analyze with specific pattern
loghero batch /var/log --pattern "auth*" --recursive
```

### Command Options

#### `loghero scan`
- `--output, -o`: Output format (table, json, csv)
- `--severity, -s`: Filter by minimum severity (LOW, MEDIUM, HIGH, CRITICAL)
- `--threat-type, -t`: Filter by specific threat type
- `--limit, -l`: Limit number of results (default: 50)
- `--quiet, -q`: Suppress banner and extra output
- `--save-report`: Save detailed report to file

#### `loghero batch`
- `--pattern, -p`: File pattern to match (default: *.log)
- `--recursive, -r`: Search recursively in subdirectories

## 🔍 Detected Threats

### SSH Brute-Force Attacks
- Failed password attempts
- Failed public key authentication
- Invalid user attempts
- Suspicious connection patterns

### Root Access Violations
- Failed `su` attempts to root
- Unauthorized `sudo` usage
- Direct root login attempts
- Privilege escalation attempts

### Authentication Failures
- Repeated login failures
- PAM authentication errors
- System authentication violations

## 📊 Example Output

```
╔══════════════════════════════════════════════════════════════╗
║                          LogHero v1.0.0                     ║
║                  System Log Security Analyzer               ║
║              Detecting suspicious activities...             ║
╚══════════════════════════════════════════════════════════════╝

📁 Analyzing log file: /var/log/auth.log

📊 Analysis Summary:
   • Total log entries processed: 15,432
   • Total threats found: 23
   • Unique source IPs: 8

🚨 Security Threats Detected:
┌─────────────────────┬──────────┬─────────────────────┬─────────────┬──────────────────────────────────┬───────┐
│ Timestamp           │ Severity │ Type                │ Source IP   │ Description                      │ Count │
├─────────────────────┼──────────┼─────────────────────┼─────────────┼──────────────────────────────────┼───────┤
│ 2024-01-15 14:23:45 │ CRITICAL │ SSH_BRUTE_FORCE     │ 192.168.1.100│ SSH brute-force attack: 25 fail...│ 25    │
│ 2024-01-15 13:45:12 │ HIGH     │ ROOT_LOGIN_ATTEMPT  │ 10.0.0.50   │ Failed direct root login attempt│ 1     │
└─────────────────────┴──────────┴─────────────────────┴─────────────┴──────────────────────────────────┴───────┘

🎯 Top Threatening IPs:
┌─────────────────┬─────────┬───────┬─────────────────────┐
│ IP Address      │ Threats │ Score │ Types               │
├─────────────────┼─────────┼───────┼─────────────────────┤
│ 192.168.1.100   │ 25      │ 100   │ SSH_BRUTE_FORCE     │
│ 10.0.0.50       │ 3       │ 9     │ ROOT_LOGIN_ATTEMPT  │
└─────────────────┴─────────┴───────┴─────────────────────┘

💡 Security Recommendations:
   1. Consider implementing fail2ban to automatically block IPs
   2. Use SSH key authentication instead of passwords
   3. Disable direct root login via SSH
   4. Implement SSH rate limiting
   5. Set up real-time alerts for security events
```

## 🗂 Supported Log Formats

### Linux
- `/var/log/auth.log` (Debian/Ubuntu)
- `/var/log/secure` (RedHat/CentOS)
- `/var/log/syslog`
- Custom syslog formats

### macOS
- `/var/log/system.log`
- `/var/log/auth.log`
- Console app logs

### Windows
- Security Event Logs
- Application Event Logs
- System Event Logs

## 🔧 Configuration

LogHero works out of the box with sensible defaults, but you can customize detection thresholds:

### SSH Brute-Force Detection
- Default threshold: 5 failed attempts
- Default time window: 300 seconds (5 minutes)

### Root Access Detection
- Monitors all `su`, `sudo`, and direct root login attempts
- Flags suspicious administrative commands

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development
# Test PyPI'dan install et
pip install --index-url https://test.pypi.org/simple/ AhmetX-LogHero/loghero.git
cd loghero
pip install -e ".[dev]"

### Running Tests
```bash
pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://loghero.readthedocs.io](https://loghero.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/ahmetxhero/AhmetX-LogHero/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ahmetxhero/AhmetX-LogHero/discussions)
- **Developer**: [AhmetXHero](https://ahmetxhero.web.app/) - [YouTube](https://www.youtube.com/@ahmetxhero) - [LinkedIn](https://www.linkedin.com/in/ahmetxhero)

## 🙏 Acknowledgments

- Thanks to the cybersecurity community for threat intelligence
- Inspired by fail2ban and other security monitoring tools
- Built with love for system administrators and security professionals

## 👨‍💻 About the Developer

**Ahmet KAHRAMAN (AhmetXHero)** is a Mobile Developer & Cyber Security Expert with 10+ years of experience in Public Sector IT. He specializes in:

- 📱 **Mobile Development**: iOS, Android, Flutter, React Native
- 🔒 **Cybersecurity**: Digital Forensics, Penetration Testing, Security Analysis
- 🎓 **Education**: Master's in Forensic Informatics, Multiple certifications
- 🌐 **Connect**: [Portfolio](https://ahmetxhero.web.app/) | [YouTube](https://www.youtube.com/@ahmetxhero) | [LinkedIn](https://www.linkedin.com/in/ahmetxhero)

*"Security first, innovation always"* 🚀

---

**⚠️ Security Notice**: LogHero is a detection tool. Always implement proper security measures like firewalls, intrusion prevention systems, and regular security updates alongside log monitoring.
