# Apps Stack - Additional Services

## Overview

This stack contains additional applications and services that complement the main self-hosted infrastructure.

## Services

### MeTube (Port 8085)
- **Purpose**: YouTube video downloader with web interface
- **Image**: `ghcr.io/alexta69/metube`
- **Access**: http://localhost:8085

### qBittorrent (Port 8086)
- **Purpose**: BitTorrent client with web interface
- **Image**: `lscr.io/linuxserver/qbittorrent:latest`
- **Access**: http://localhost:8086

### OpenSpeedTest (Port 3002)
- **Purpose**: Network speed testing with automated scheduling
- **Image**: `openspeedtest/latest:latest`
- **Access**: http://localhost:3002
- **Database**: MariaDB (shared with Nextcloud stack)

### SpeedTest Scheduler
- **Purpose**: Automated speed test execution every hour
- **Type**: Custom Python container
- **Database**: Saves results to MariaDB

## OpenSpeedTest Automation

### Features
- **Automated Testing**: Executes speed tests every hour
- **Database Storage**: Results saved to dedicated MariaDB database
- **Comprehensive Logging**: Detailed logs for monitoring
- **Error Handling**: Robust error handling and retry logic

### Database Schema
The scheduler creates a `speedtest_results` table with the following structure:

```sql
CREATE TABLE speedtest_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    test_date DATETIME NOT NULL,
    download_speed DECIMAL(10,2),
    upload_speed DECIMAL(10,2),
    ping_latency DECIMAL(10,2),
    jitter DECIMAL(10,2),
    server_info TEXT,
    client_ip VARCHAR(45),
    user_agent TEXT,
    test_duration INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Environment Variables
```bash
# Database Configuration
MYSQL_HOST=host.docker.internal
MYSQL_PORT=3306
OPENSPEEDTEST_DB_NAME=openspeedtest
OPENSPEEDTEST_DB_USER=openspeedtest_user
OPENSPEEDTEST_DB_PASSWORD=OpenSpeedTest123
```

## Deployment

### Prerequisites
1. MariaDB container running (from Nextcloud stack)
2. OpenSpeedTest database and user created

### Setup
```bash
# Navigate to apps directory
cd apps

# Start all services
docker compose up -d

# Check logs
docker compose logs -f speedtest-scheduler
```

### Database Setup
The database and user are automatically created when you run:
```bash
docker exec -i mariadb mysql -u root -p39DUz80peh8CPn2e -e "
CREATE DATABASE IF NOT EXISTS openspeedtest; 
CREATE USER IF NOT EXISTS 'openspeedtest_user'@'%' IDENTIFIED BY 'OpenSpeedTest123'; 
GRANT ALL PRIVILEGES ON openspeedtest.* TO 'openspeedtest_user'@'%'; 
FLUSH PRIVILEGES;"
```

## Monitoring

### View Speed Test Results
```sql
-- Connect to MariaDB
docker exec -it mariadb mysql -u openspeedtest_user -pOpenSpeedTest123 openspeedtest

-- View recent results
SELECT 
    test_date,
    download_speed,
    upload_speed,
    ping_latency,
    jitter
FROM speedtest_results 
ORDER BY test_date DESC 
LIMIT 10;

-- Average speeds by day
SELECT 
    DATE(test_date) as test_day,
    AVG(download_speed) as avg_download,
    AVG(upload_speed) as avg_upload,
    AVG(ping_latency) as avg_ping
FROM speedtest_results 
GROUP BY DATE(test_date)
ORDER BY test_day DESC;
```

### Scheduler Logs
```bash
# View scheduler logs
docker compose logs speedtest-scheduler

# Follow logs in real-time
docker compose logs -f speedtest-scheduler

# View specific time range
docker compose logs --since="1h" speedtest-scheduler
```

## Troubleshooting

### Common Issues

**Scheduler Not Running Tests**
```bash
# Check scheduler status
docker compose ps speedtest-scheduler

# Check logs for errors
docker compose logs speedtest-scheduler

# Restart scheduler
docker compose restart speedtest-scheduler
```

**Database Connection Issues**
```bash
# Test database connectivity
docker exec speedtest-scheduler python -c "
import mysql.connector
conn = mysql.connector.connect(
    host='host.docker.internal',
    port=3306,
    database='openspeedtest',
    user='openspeedtest_user',
    password='OpenSpeedTest123'
)
print('Database connection successful')
conn.close()
"
```

**OpenSpeedTest API Issues**
```bash
# Test OpenSpeedTest API
curl -X POST http://localhost:3002/api/start

# Check OpenSpeedTest logs
docker compose logs openspeedtest
```

## Customization

### Change Test Frequency
Edit `speedtest-scheduler/scheduler.py`:
```python
# Change from every hour to every 30 minutes
schedule.every(30).minutes.do(self.execute_scheduled_test)

# Or every 6 hours
schedule.every(6).hours.do(self.execute_scheduled_test)
```

### Add Custom Metrics
Extend the database schema and scheduler to capture additional metrics:
```sql
ALTER TABLE speedtest_results 
ADD COLUMN location VARCHAR(100),
ADD COLUMN isp_name VARCHAR(100);
```

## Integration

### Grafana Dashboard
Create dashboards to visualize speed test data:
- Download/Upload speed trends
- Latency and jitter monitoring
- Historical performance analysis

### Prometheus Metrics
Consider adding Prometheus metrics export for integration with monitoring stack.

## Maintenance

### Regular Tasks
```bash
# Update containers
docker compose pull
docker compose up -d

# Clean old test results (older than 90 days)
docker exec -i mariadb mysql -u openspeedtest_user -pOpenSpeedTest123 openspeedtest -e "
DELETE FROM speedtest_results 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);"

# Backup speed test data
docker exec mariadb mysqldump -u openspeedtest_user -pOpenSpeedTest123 openspeedtest > speedtest_backup.sql
```

### Log Rotation
Logs are automatically rotated with the configured Docker logging driver (10MB max, 3 files).
