# Quick Start Guide

Get your SIEM Dashboard up and running in under 10 minutes!

## Prerequisites

Ensure you have the following installed:
- Docker and Docker Compose
- Python 3.8 or higher
- At least 4GB of available RAM

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/siem-dashboard.git
cd siem-dashboard

# Install Python dependencies
pip install -r requirements.txt
```

## Step 2: Start the ELK Stack

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs (optional)
docker-compose logs -f
```

Wait 2-3 minutes for all services to fully start.

## Step 3: Verify Services

Check that all services are running:

```bash
# Elasticsearch
curl -u elastic:changeme http://localhost:9200

# Kibana
curl http://localhost:5601/api/status

# Logstash
curl http://localhost:9600
```

## Step 4: Initialize SIEM

Run the setup script to create indices, templates, and load detection rules:

```bash
python scripts/setup_siem.py
```

This script will:
- Create index templates
- Set up lifecycle policies
- Load detection rules
- Configure Kibana index patterns

## Step 5: Generate Test Data

Create sample security events to test the system:

```bash
python scripts/generate_test_logs.py
```

This will generate:
- Brute force attacks
- SQL injection attempts
- Port scans
- Data exfiltration events
- Normal activity logs

## Step 6: Access Kibana

1. Open your browser to http://localhost:5601
2. Login with:
   - Username: `elastic`
   - Password: `changeme`
3. Navigate to **Discover** to view logs
4. Navigate to **Dashboard** to see visualizations

## Step 7: Explore Detection Rules

View active detection rules:

```bash
# List all detection rules
curl -u elastic:changeme \
  http://localhost:9200/detection-rules/_search?pretty
```

## Common Commands

### View Logs
```bash
# Elasticsearch logs
docker-compose logs elasticsearch

# Logstash logs
docker-compose logs logstash

# Kibana logs
docker-compose logs kibana
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart logstash
```

### Stop Everything
```bash
# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

## Sending Custom Logs

### Via TCP (JSON)
```bash
echo '{"message":"Test event","severity":"high"}' | nc localhost 5000
```

### Via Syslog
```bash
logger -n localhost -P 5514 "Test syslog message"
```

### Via Python
```python
import socket
import json

log_event = {
    "@timestamp": "2024-12-17T10:00:00Z",
    "message": "Security test event",
    "source": {"ip": "192.168.1.100"},
    "severity": "medium"
}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 5000))
sock.send(json.dumps(log_event).encode() + b'\n')
sock.close()
```

## Troubleshooting

### Elasticsearch won't start
```bash
# Check memory settings
docker stats

# Increase Docker memory to at least 4GB in Docker settings
```

### Cannot connect to Kibana
```bash
# Wait longer (can take 3-5 minutes on first start)
docker-compose logs kibana | grep "Server running"
```

### Logs not appearing
```bash
# Check Logstash pipeline
docker-compose logs logstash | grep ERROR

# Test Logstash connectivity
telnet localhost 5000
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d
python scripts/setup_siem.py
```

## Next Steps

1. **Customize Detection Rules**: Edit files in `detection-rules/`
2. **Configure Alerts**: Set up email/webhook notifications in `config/alerts.yml`
3. **Add Data Sources**: Configure your systems to send logs to Logstash
4. **Create Dashboards**: Build custom visualizations in Kibana
5. **Review Documentation**: Check the `docs/` folder for detailed guides

## Security Reminder

**Before using in production:**

1. Change default passwords in `docker-compose.yml`
2. Enable SSL/TLS encryption
3. Configure firewall rules
4. Set up proper authentication
5. Review and harden security settings

## Getting Help

- Check logs: `docker-compose logs`
- Review documentation in `docs/`
- Open an issue on GitHub
- Check Elastic Stack documentation

## Resource Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4GB
- Disk: 20GB

**Recommended:**
- CPU: 4 cores
- RAM: 8GB
- Disk: 100GB (with proper retention policies)

---

🎉 **Congratulations!** Your SIEM Dashboard is now running!
