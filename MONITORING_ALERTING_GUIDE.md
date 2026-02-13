# Monitoring & Alerting Guide - Authentication System

## Overview
This guide covers monitoring, alerting, and incident response for the authentication system.

---

## 📊 **Monitoring Architecture**

### **Monitoring Stack:**
- **Application Metrics**: Django application performance
- **System Metrics**: Server resources (CPU, memory, disk)
- **Security Monitoring**: Authentication attempts, suspicious activity
- **Audit Logging**: User activity tracking
- **Database Monitoring**: Query performance, connection health
- **API Monitoring**: Endpoint availability and response times

### **Tools Required:**
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert routing and management
- **ELK Stack**: Log aggregation and analysis
- **Nagios/Icinga**: Infrastructure monitoring

---

## 🔧 **Application Monitoring Setup**

### **Django Metrics Configuration**

```python
# settings.py - Add monitoring
INSTALLED_APPS = [
    # ... existing apps
    'django_prometheus',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
    # ... other middleware
]

# Health check URLs
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN': 100,    # in MB
}

# Prometheus metrics
PROMETHEUS_METRICS_EXPORT_PORT = 8001
PROMETHEUS_METRICS_EXPORT_ADDRESS = '0.0.0.0'
```

### **Custom Metrics for Authentication**

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
from django.conf import settings

# Authentication metrics
LOGIN_ATTEMPTS = Counter(
    'authentication_login_attempts_total',
    'Total login attempts',
    ['status', 'user_role']
)

LOGIN_DURATION = Histogram(
    'authentication_login_duration_seconds',
    'Login request duration',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

ACTIVE_SESSIONS = Gauge(
    'authentication_active_sessions',
    'Number of active user sessions'
)

FAILED_LOGINS = Counter(
    'authentication_failed_logins_total',
    'Total failed login attempts',
    ['reason']
)

# Permission metrics
PERMISSION_DENIED = Counter(
    'authentication_permission_denied_total',
    'Permission denied attempts',
    ['endpoint', 'user_role', 'required_role']
)

# Audit metrics
AUDIT_EVENTS = Counter(
    'audit_events_total',
    'Total audit events',
    ['event_type', 'user_role']
)

# Messaging metrics
MESSAGES_SENT = Counter(
    'messaging_messages_sent_total',
    'Messages sent',
    ['sender_role', 'recipient_role']
)

# Upload metrics
UPLOADS_PROCESSED = Counter(
    'uploads_processed_total',
    'File uploads processed',
    ['status', 'file_type']
)
```

### **Metrics Collection in Views**

```python
# api/views.py - Add metrics to authentication views
from monitoring.metrics import LOGIN_ATTEMPTS, LOGIN_DURATION, FAILED_LOGINS

class CustomTokenObtainPairView(TokenObtainPairView):
    @LOGIN_DURATION.time()
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)

            if response.status_code == 200:
                user = authenticate(
                    username=request.data.get('username'),
                    password=request.data.get('password')
                )
                if user:
                    LOGIN_ATTEMPTS.labels(
                        status='success',
                        user_role=user.role
                    ).inc()
                else:
                    FAILED_LOGINS.labels(reason='invalid_credentials').inc()
                    LOGIN_ATTEMPTS.labels(status='failed', user_role='unknown').inc()
            else:
                FAILED_LOGINS.labels(reason='invalid_request').inc()
                LOGIN_ATTEMPTS.labels(status='failed', user_role='unknown').inc()

            return response
        except Exception as e:
            FAILED_LOGINS.labels(reason='error').inc()
            raise
```

---

## 📈 **Grafana Dashboard Setup**

### **Authentication Dashboard**

#### **Key Metrics to Monitor:**
1. **Login Success Rate**
   ```
   rate(authentication_login_attempts_total{status="success"}[5m]) /
   rate(authentication_login_attempts_total[5m]) * 100
   ```

2. **Failed Login Attempts**
   ```
   increase(authentication_failed_logins_total[1h])
   ```

3. **Active Sessions**
   ```
   authentication_active_sessions
   ```

4. **Permission Denied Events**
   ```
   increase(authentication_permission_denied_total[1h])
   ```

5. **Response Time**
   ```
   histogram_quantile(0.95, rate(authentication_login_duration_seconds_bucket[5m]))
   ```

### **Security Dashboard**

#### **Security Metrics:**
1. **Suspicious Login Patterns**
   ```
   rate(authentication_failed_logins_total{reason="invalid_credentials"}[1h])
   ```

2. **Brute Force Attempts**
   ```
   increase(authentication_failed_logins_total{reason="invalid_credentials"}[5m]) > 10
   ```

3. **Unauthorized Access Attempts**
   ```
   increase(authentication_permission_denied_total[1h])
   ```

### **System Health Dashboard**

#### **Infrastructure Metrics:**
1. **Application Response Time**
2. **Database Connection Pool**
3. **Memory Usage**
4. **Disk Space**
5. **Error Rates**

---

## 🚨 **Alerting Configuration**

### **Alertmanager Configuration**

```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@yourdomain.com'
  smtp_auth_username: 'alerts@yourdomain.com'
  smtp_auth_password: 'your-app-password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'team-alerts'
  routes:
  - match:
      severity: critical
    receiver: 'critical-alerts'

receivers:
- name: 'team-alerts'
  email_configs:
  - to: 'team@yourdomain.com'
    subject: '{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}'
    body: '{{ .CommonAnnotations.description }}'

- name: 'critical-alerts'
  email_configs:
  - to: 'admin@yourdomain.com'
    subject: 'CRITICAL: {{ .GroupLabels.alertname }}'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    channel: '#alerts'
    title: 'CRITICAL ALERT'
    text: '{{ .CommonAnnotations.description }}'
```

### **Prometheus Alerting Rules**

```yaml
# alerting_rules.yml
groups:
- name: authentication_alerts
  rules:

  # High failure rate
  - alert: HighLoginFailureRate
    expr: rate(authentication_failed_logins_total[5m]) / rate(authentication_login_attempts_total[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High login failure rate detected"
      description: "Login failure rate is {{ $value | printf \"%.2f\" }}% over the last 5 minutes"

  # Brute force detection
  - alert: BruteForceAttack
    expr: increase(authentication_failed_logins_total{reason="invalid_credentials"}[5m]) > 20
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Potential brute force attack detected"
      description: "{{ $value | printf \"%.0f\" }} failed login attempts in 5 minutes"

  # Permission violations
  - alert: ExcessivePermissionDenied
    expr: increase(authentication_permission_denied_total[10m]) > 50
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High number of permission denied events"
      description: "{{ $value | printf \"%.0f\" }} permission denied events in 10 minutes"

  # System health
  - alert: ApplicationDown
    expr: up{job="antibiogram"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Application is down"
      description: "Antibiogram application has been down for more than 1 minute"

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="antibiogram"}[5m])) > 5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value | printf \"%.2f\" }}s"

  # Database issues
  - alert: DatabaseConnectionIssues
    expr: rate(django_db_errors_total[5m]) > 5
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Database connection issues detected"
      description: "{{ $value | printf \"%.0f\" }} database errors in 5 minutes"
```

---

## 📋 **Log Aggregation Setup**

### **ELK Stack Configuration**

#### **Filebeat Configuration**
```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/www/antibiogram/logs/*.log
  fields:
    service: antibiogram
    environment: production

- type: log
  enabled: true
  paths:
    - /var/log/nginx/*.log
  fields:
    service: nginx
    environment: production

processors:
- add_host_metadata:
    when.not.contains.tags: forwarded
- add_cloud_metadata: ~
- add_docker_metadata: ~
- add_kubernetes_metadata: ~

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "antibiogram-%{+yyyy.MM.dd}"
```

#### **Logstash Pipeline**
```ruby
# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "antibiogram" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{DATA:module} %{GREEDYDATA:message}" }
    }

    # Parse authentication events
    if [message] =~ /LOGIN/ {
      grok {
        match => { "message" => "LOGIN: user=%{USERNAME:user} ip=%{IP:ip} success=%{WORD:success}" }
      }
      mutate {
        add_tag => ["authentication"]
      }
    }

    # Parse audit events
    if [message] =~ /AUDIT/ {
      grok {
        match => { "message" => "AUDIT: user=%{USERNAME:user} action=%{WORD:action} resource=%{DATA:resource}" }
      }
      mutate {
        add_tag => ["audit"]
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "antibiogram-%{+YYYY.MM.dd}"
  }
}
```

#### **Kibana Dashboards**
Create dashboards for:
- Authentication events over time
- Failed login attempts by IP
- User activity patterns
- Error rates and types
- Performance metrics

---

## 🔍 **Security Monitoring**

### **Intrusion Detection**

#### **Fail2Ban Configuration**
```ini
# /etc/fail2ban/jail.local
[antibiogram-auth]
enabled = true
port = http,https
filter = antibiogram-auth
logpath = /var/www/antibiogram/logs/django.log
maxretry = 5
bantime = 3600
findtime = 600

# Custom filter for authentication failures
# /etc/fail2ban/filter.d/antibiogram-auth.conf
[Definition]
failregex = ^.*LOGIN.*user=.*ip=<HOST>.*success=False.*$
ignoreregex =
```

#### **OSSEC Configuration**
```xml
<!-- /var/ossec/etc/ossec.conf -->
<localfile>
  <log_format>syslog</log_format>
  <location>/var/www/antibiogram/logs/django.log</location>
</localfile>

<localfile>
  <log_format>syslog</log_format>
  <location>/var/log/nginx/access.log</location>
</localfile>

<!-- Custom rules for authentication -->
<group name="authentication,">
  <rule id="100001" level="5">
    <if_sid>5716</if_sid>
    <match>LOGIN.*success=False</match>
    <description>Failed login attempt</description>
  </rule>

  <rule id="100002" level="10">
    <if_sid>100001</if_sid>
    <match>ip=</match>
    <check_diff />
    <description>Multiple failed login attempts from same IP</description>
  </rule>
</group>
```

### **Anomaly Detection**

#### **Custom Scripts for Suspicious Activity**
```python
# monitoring/anomaly_detector.py
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from audit.models import LoginLog

def detect_brute_force():
    """Detect potential brute force attacks"""
    # Check for IPs with high failure rates in last hour
    one_hour_ago = datetime.now() - timedelta(hours=1)

    failed_attempts = LoginLog.objects.filter(
        timestamp__gte=one_hour_ago,
        success=False
    ).values('ip_address').annotate(
        count=models.Count('id')
    ).filter(count__gt=10)

    for attempt in failed_attempts:
        logger.warning(f"Potential brute force from IP: {attempt['ip_address']}")

def detect_unusual_activity():
    """Detect unusual user behavior"""
    # Check for users logging in from multiple countries
    # Check for users accessing data outside normal hours
    # Check for unusual data export volumes

def detect_permission_abuse():
    """Detect potential permission abuse"""
    # Check for users repeatedly hitting forbidden endpoints
    # Check for users accessing data they don't normally access
```

---

## 📊 **Incident Response**

### **Incident Response Plan**

#### **Phase 1: Detection & Assessment (0-15 minutes)**
1. **Alert Received**: Monitoring system detects anomaly
2. **Initial Assessment**: Determine severity and scope
3. **Team Notification**: Alert relevant personnel
4. **Containment**: Isolate affected systems if needed

#### **Phase 2: Investigation (15-60 minutes)**
1. **Log Analysis**: Review audit logs and system logs
2. **Scope Determination**: Identify affected users/data
3. **Root Cause Analysis**: Determine how incident occurred
4. **Evidence Collection**: Preserve forensic data

#### **Phase 3: Containment & Recovery (1-4 hours)**
1. **System Isolation**: Disconnect compromised systems
2. **Password Reset**: Force password changes for affected users
3. **Access Revocation**: Disable suspicious accounts
4. **Data Backup**: Ensure clean backups are available
5. **System Restoration**: Restore from clean backups

#### **Phase 4: Post-Incident Analysis (4-24 hours)**
1. **Timeline Creation**: Document incident timeline
2. **Impact Assessment**: Determine data exposure and damage
3. **Lessons Learned**: Identify prevention measures
4. **Report Generation**: Create incident report

### **Communication Templates**

#### **Internal Incident Notification**
```
Subject: SECURITY INCIDENT - [Incident Type] Detected

Incident Details:
- Time Detected: [Timestamp]
- Affected Systems: [Systems]
- Potential Impact: [Impact Assessment]
- Current Status: [Investigation/Contained/Resolved]

Actions Taken:
- [List immediate actions]

Next Steps:
- [Investigation plan]
- [Communication plan]

Contact: [Incident Response Team]
```

#### **User Notification Template**
```
Subject: Important Security Notice - Account Security

Dear [User Name],

We detected unusual activity on your account. For your security, we have:

1. Temporarily suspended your account access
2. Required a password reset
3. Enabled additional security measures

To restore access:
1. Visit [Password Reset Link]
2. Create a new strong password
3. Enable two-factor authentication if available

If you did not initiate this activity, please contact us immediately.

Security Team
[Contact Information]
```

---

## 📈 **Performance Monitoring**

### **Key Performance Indicators (KPIs)**

#### **Authentication KPIs**
- **Login Success Rate**: > 95%
- **Average Login Time**: < 2 seconds
- **Failed Login Rate**: < 5%
- **Session Duration**: Average user session time

#### **Security KPIs**
- **Brute Force Attempts**: < 10 per hour
- **Permission Violations**: < 50 per day
- **Suspicious IPs**: Monitored and blocked
- **Security Incidents**: < 1 per month

#### **System KPIs**
- **Uptime**: > 99.5%
- **Response Time**: < 1 second (95th percentile)
- **Error Rate**: < 1%
- **Resource Usage**: < 80% capacity

### **Regular Monitoring Tasks**

#### **Daily Checks**
- [ ] Review failed login attempts
- [ ] Check system resource usage
- [ ] Verify backup completion
- [ ] Review security alerts

#### **Weekly Checks**
- [ ] Analyze user activity patterns
- [ ] Review audit logs for anomalies
- [ ] Update security signatures
- [ ] Test backup restoration

#### **Monthly Checks**
- [ ] Security vulnerability assessment
- [ ] Performance optimization review
- [ ] Compliance audit preparation
- [ ] User access review

---

## 🔧 **Maintenance Procedures**

### **Regular Maintenance Tasks**

#### **Security Updates**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
cd /var/www/antibiogram
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Restart services
sudo systemctl restart antibiogram
sudo systemctl restart nginx
```

#### **Log Rotation**
```bash
# Check log sizes
du -sh /var/www/antibiogram/logs/*

# Manual rotation if needed
sudo logrotate -f /etc/logrotate.d/antibiogram

# Archive old logs
find /var/log/antibiogram -name "*.log.*" -mtime +30 -delete
```

#### **Database Maintenance**
```bash
# Vacuum and analyze database
python manage.py vacuumdb

# Check database size
python manage.py dbshell -c "SELECT pg_size_pretty(pg_database_size('antibiogram_db'));"

# Archive old audit data (if needed)
python manage.py archive_old_audit_data
```

---

## 📞 **Contact Information**

### **Monitoring Team**
- **Primary Contact**: [Monitoring Lead]
- **Backup Contact**: [Deputy Monitor]
- **On-Call Schedule**: [Rotation Schedule]

### **Security Team**
- **Security Officer**: [CSO Contact]
- **Incident Response**: [IRT Contact]
- **Forensic Analysis**: [Forensics Team]

### **Vendor Contacts**
- **Cloud Provider**: [AWS/Azure Support]
- **Security Tools**: [Vendor Support]
- **Monitoring Tools**: [Tool Support]

---

## ✅ **Monitoring Checklist**

### **Initial Setup**
- [ ] Prometheus installed and configured
- [ ] Grafana dashboards created
- [ ] Alertmanager rules configured
- [ ] ELK stack deployed
- [ ] Application metrics enabled
- [ ] Security monitoring active

### **Ongoing Monitoring**
- [ ] Daily alert review
- [ ] Weekly performance analysis
- [ ] Monthly security assessment
- [ ] Quarterly compliance audit
- [ ] Annual disaster recovery test

---

**🎯 Monitoring system is now active and will ensure the security and reliability of your authentication system.**
