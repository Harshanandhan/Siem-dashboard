# SIEM Dashboard - Security Information and Event Management System

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Docker](https://img.shields.io/badge/docker-enabled-brightgreen.svg)

A comprehensive Security Information and Event Management (SIEM) solution built with the ELK Stack (Elasticsearch, Logstash, Kibana) for real-time security monitoring, log analysis, and threat detection.

## 🎯 Project Overview

This SIEM Dashboard provides:
- Real-time log collection and analysis
- Automated threat detection rules
- Interactive security dashboards
- Alert management system
- Incident response workflows
- Compliance reporting capabilities

## 🏗️ Architecture

```
┌─────────────────┐
│  Log Sources    │
│  - Firewalls    │
│  - Web Servers  │
│  - Applications │
│  - System Logs  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Logstash      │
│  (Data Ingestion│
│   & Processing) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Elasticsearch   │
│ (Data Storage & │
│    Indexing)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Kibana      │
│  (Visualization │
│   & Dashboard)  │
└─────────────────┘
```

## 🚀 Features

### Core Capabilities
- **Multi-source Log Ingestion**: Collect logs from various sources (syslog, filebeat, API)
- **Real-time Threat Detection**: Pre-configured detection rules for common attacks
- **Custom Dashboards**: Security-focused visualizations and metrics
- **Alert System**: Email and webhook notifications for critical events
- **Search & Investigation**: Powerful query interface for incident investigation
- **Compliance Reporting**: Pre-built reports for common frameworks (PCI-DSS, HIPAA)

### Detection Rules
- Brute Force Attack Detection
- SQL Injection Attempts
- Port Scanning Activity
- Suspicious Login Patterns
- Data Exfiltration Indicators
- Malware Communication Patterns
- Privilege Escalation Attempts
- Failed Authentication Tracking

## 📋 Prerequisites

- Docker and Docker Compose (recommended)
- OR Manual installation:
  - Elasticsearch 8.x
  - Logstash 8.x
  - Kibana 8.x
  - Python 3.8+
- Minimum 4GB RAM (8GB recommended)
- 20GB free disk space

## 🛠️ Installation

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/siem-dashboard.git
cd siem-dashboard

# Start the ELK stack
docker-compose up -d

# Wait for services to start (2-3 minutes)
docker-compose ps

# Access Kibana at http://localhost:5601
# Default credentials: elastic / changeme
```

### Option 2: Manual Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure Elasticsearch
sudo systemctl start elasticsearch

# Configure Logstash
sudo systemctl start logstash

# Configure Kibana
sudo systemctl start kibana

# Import dashboards and detection rules
python scripts/setup_siem.py
```

## 📊 Configuration

### 1. Configure Log Sources

Edit `logstash/pipeline/logstash.conf` to add your log sources:

```conf
input {
  # Syslog input
  syslog {
    port => 5514
  }
  
  # File input
  file {
    path => "/var/log/secure"
    type => "linux-secure"
  }
}
```

### 2. Customize Detection Rules

Detection rules are located in `detection-rules/`. Each rule is a JSON file:

```json
{
  "name": "Brute Force Detection",
  "query": "event.category:authentication AND event.outcome:failure",
  "threshold": 5,
  "timeframe": "5m"
}
```

### 3. Set Up Alerts

Configure email alerts in `config/alerts.yml`:

```yaml
alerts:
  email:
    smtp_host: smtp.gmail.com
    smtp_port: 587
    from: siem@yourdomain.com
    to: security-team@yourdomain.com
```

## 📈 Usage

### Accessing the Dashboard

1. Open browser to `http://localhost:5601`
2. Login with credentials (default: elastic/changeme)
3. Navigate to Dashboard → SIEM Overview

### Sending Test Logs

```bash
# Generate sample security events
python scripts/generate_test_logs.py

# Send logs via syslog
logger -n localhost -P 5514 "Test security event"

# Import sample dataset
python scripts/import_sample_data.py
```

### Investigating Security Events

1. Go to Discover → Select index pattern `logs-*`
2. Use KQL queries:
   - Failed logins: `event.outcome:failure AND event.category:authentication`
   - Port scans: `event.category:network AND source.port:* AND destination.port:[1 TO 1024]`
   - SQL injection: `url.path:*UNION* OR url.path:*SELECT*`

### Creating Custom Dashboards

1. Navigate to Dashboard → Create New Dashboard
2. Add visualizations (pie charts, line graphs, data tables)
3. Save and share with your team

## 🔒 Security Best Practices

- **Change Default Passwords**: Immediately update the elastic user password
- **Enable TLS/SSL**: Configure encryption for all communications
- **Implement RBAC**: Set up role-based access control
- **Regular Updates**: Keep ELK stack components updated
- **Backup Configuration**: Regular backups of Elasticsearch indices
- **Network Segmentation**: Restrict access to SIEM infrastructure

## 📁 Project Structure

```
siem-dashboard/
├── README.md
├── docker-compose.yml
├── requirements.txt
├── config/
│   ├── elasticsearch.yml
│   ├── kibana.yml
│   └── alerts.yml
├── logstash/
│   ├── pipeline/
│   │   └── logstash.conf
│   └── patterns/
│       └── custom-patterns.txt
├── detection-rules/
│   ├── brute_force.json
│   ├── sql_injection.json
│   ├── port_scan.json
│   └── data_exfiltration.json
├── dashboards/
│   ├── security_overview.ndjson
│   ├── threat_hunting.ndjson
│   └── compliance_report.ndjson
├── scripts/
│   ├── setup_siem.py
│   ├── generate_test_logs.py
│   ├── import_sample_data.py
│   └── backup_config.py
└── docs/
    ├── ARCHITECTURE.md
    ├── DETECTION_RULES.md
    ├── TROUBLESHOOTING.md
    └── API_REFERENCE.md
```

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/

# Test detection rules
python scripts/test_detection_rules.py

# Generate test alerts
python scripts/trigger_test_alerts.py
```

## 📚 Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [Detection Rules Guide](docs/DETECTION_RULES.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [API Reference](docs/API_REFERENCE.md)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-detection-rule`)
3. Commit changes (`git commit -m 'Add new detection rule'`)
4. Push to branch (`git push origin feature/new-detection-rule`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- ELK Stack by Elastic
- Detection rules inspired by MITRE ATT&CK framework
- Community contributors and security researchers

## 📧 Contact

- **Author 1**: Harshanandhan Reddy Gajulapalli
- **Email**: harshanandhan820@gmail.com
- **Author 2**: Charitha Arigela
- **Email**: 
- **LinkedIn 1**:
- **LinkedIn 2**: 


## 🔄 Changelog

### Version 1.0.0 (2024-12-17)
- Initial release
- Core SIEM functionality
- 5 pre-configured detection rules
- 3 security dashboards
- Docker support

---

**⚠️ Disclaimer**: This is a learning project for educational purposes. For production environments, conduct thorough security assessments and follow your organization's security policies.
