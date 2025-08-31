# Self-Hosted Projects

A comprehensive collection of self-hosted services running on Docker, providing personal cloud storage, network security, monitoring, and development tools.

## 🚀 Services Overview

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| [Nextcloud](./docs/memory-bank/services/nextcloud.md) | 8080 | Personal cloud storage and collaboration | ✅ Active |
| [Pi-hole + Unbound](./docs/memory-bank/services/pihole-unbound.md) | 80, 53 | Network-wide ad blocking and DNS resolution | ✅ Active |
| [Homer](./docs/memory-bank/services/homer.md) | 8081 | Static homepage and service dashboard | ✅ Active |
| [Uptime Kuma](./docs/memory-bank/services/uptimekuma.md) | 3001 | Self-hosted monitoring and alerting | ✅ Active |
| [Cloudflare Tunnel](./docs/memory-bank/services/cloudflare-tunnel.md) | - | Secure remote access without port forwarding | ✅ Active |
| [VS Code Server](./docs/memory-bank/services/vscode-server.md) | - | Web-based development environment | 📋 Configured |

## 📁 Project Structure

```
self-hosted-projects/
├── backup/                     # Automated backup system
│   ├── backup.sh              # Main backup script
│   └── log/                   # Backup operation logs
├── cloudflaretunnel/          # Cloudflare Tunnel configuration
├── homer/                     # Homepage dashboard
├── nextcloud/                 # Personal cloud platform
├── pihole-unbound/           # DNS filtering and resolution
├── uptimekuma/               # Service monitoring
├── vscodeserver/             # Development environment
└── docs/                     # Documentation and memory bank
    └── memory-bank/          # Comprehensive service documentation
```

## 🔧 Prerequisites

### System Requirements
- **OS**: Linux (tested on Ubuntu/Debian)
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Storage**: Minimum 20GB available space
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Network**: Static IP recommended for DNS services

### Installation
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/carloseduardoveloso/self-hosted-projects.git
cd self-hosted-projects
```

### 2. Environment Configuration
Create environment files for each service:

```bash
# Nextcloud environment
cat > nextcloud/.env << EOF
TZ=America/Sao_Paulo
MYSQL_DATABASE=nextcloud
MYSQL_USER=nextcloud
MYSQL_PASSWORD=secure_database_password
NEXTCLOUD_ADMIN_USER=admin
NEXTCLOUD_ADMIN_PASSWORD=secure_admin_password
NEXTCLOUD_TRUSTED_DOMAINS=localhost,your-domain.com
EOF

# Pi-hole environment
cat > pihole-unbound/.env << EOF
TZ=America/Sao_Paulo
PIHOLE_PASSWORD=secure_pihole_password
EOF

# Cloudflare Tunnel environment
cat > cloudflaretunnel/.env << EOF
TZ=America/Sao_Paulo
CLOUDFLARE_TUNNEL_TOKEN=your_tunnel_token_here
EOF
```

### 3. Deploy Services
```bash
# Start individual services
cd nextcloud && docker compose up -d
cd ../pihole-unbound && docker compose up -d
cd ../homer && docker compose up -d
cd ../uptimekuma && docker compose up -d
cd ../cloudflaretunnel && docker compose up -d

# Or use the deployment script (if available)
./deploy-all.sh
```

### 4. Verify Deployment
```bash
# Check all services status
docker ps

# Test service accessibility
curl -I http://localhost:8080  # Nextcloud
curl -I http://localhost:80    # Pi-hole
curl -I http://localhost:8081  # Homer
curl -I http://localhost:3001  # Uptime Kuma
```

## 📚 Documentation

### Memory Bank
Comprehensive documentation is available in the [Memory Bank](./docs/memory-bank/README.md):

- **[Service Documentation](./docs/memory-bank/README.md#service-documentation)** - Detailed setup and configuration guides
- **[Operations Documentation](./docs/memory-bank/README.md#operations-documentation)** - Backup, monitoring, and maintenance procedures
- **[Troubleshooting Guides](./docs/memory-bank/README.md#troubleshooting-guides)** - Common issues and solutions
- **[Maintenance Procedures](./docs/memory-bank/README.md#maintenance-procedures)** - Regular maintenance tasks

### Quick Links
- [Nextcloud Setup Guide](./docs/memory-bank/services/nextcloud.md)
- [Pi-hole Configuration](./docs/memory-bank/services/pihole-unbound.md)
- [Backup System](./docs/memory-bank/operations/backup-system.md)
- [Common Issues](./docs/memory-bank/troubleshooting/common-issues.md)

## 🔒 Security Features

### Network Security
- **Isolated Networks**: Services use dedicated Docker networks
- **Minimal Port Exposure**: Only necessary ports exposed to host
- **DNS Filtering**: Pi-hole blocks malicious domains network-wide
- **Secure Tunneling**: Cloudflare Tunnel provides secure remote access

### Data Protection
- **Automated Backups**: Daily backups with 7-day retention
- **Data Encryption**: Database and file encryption at rest
- **Access Control**: Strong passwords and authentication
- **Health Monitoring**: Continuous service health checks

### Best Practices
- Regular security updates via container image updates
- Environment variable management for sensitive data
- Firewall configuration for additional protection
- SSL/TLS encryption for web interfaces

## 🔧 Maintenance

### Daily Tasks (Automated)
- ✅ Automated backups (2:00 AM)
- ✅ Health check monitoring
- ✅ Log rotation and cleanup
- ✅ Security updates (if auto-update enabled)

### Weekly Tasks
- [ ] Review backup logs and verify integrity
- [ ] Check service resource usage
- [ ] Update Pi-hole blocklists
- [ ] Review security logs

### Monthly Tasks
- [ ] Update container images
- [ ] Test backup restoration procedures
- [ ] Review and optimize configurations
- [ ] Security audit and updates

### Maintenance Commands
```bash
# Update all services
docker compose pull && docker compose up -d

# View service logs
docker compose logs -f [service-name]

# Check resource usage
docker stats

# Backup verification
sha256sum -c /mnt/data/backups/nextcloud-data/*.sha256
```

## 📊 Monitoring

### Health Checks
All services include comprehensive health checks:
- **Nextcloud**: HTTP endpoint monitoring
- **MariaDB**: Database connectivity verification
- **Redis**: Connection and response testing
- **Pi-hole**: DNS resolution testing
- **Unbound**: DNSSEC validation testing

### Monitoring Tools
- **Uptime Kuma**: Web-based service monitoring
- **Docker Health Checks**: Built-in container health monitoring
- **Log Analysis**: Centralized logging with rotation
- **Resource Monitoring**: CPU, memory, and disk usage tracking

### Alerting
Configure Uptime Kuma for:
- Service downtime notifications
- Performance degradation alerts
- SSL certificate expiration warnings
- Backup failure notifications

## 🔄 Backup Strategy

### Automated Backup System
- **Schedule**: Daily at 2:00 AM
- **Retention**: 7 days
- **Compression**: 7-Zip maximum compression
- **Integrity**: SHA-256 checksum verification
- **Location**: `/mnt/data/backups/nextcloud-data/`

### Manual Backup
```bash
# Run backup manually
cd backup
./backup.sh

# Verify backup integrity
sha256sum -c /mnt/data/backups/nextcloud-data/latest-backup.tar.7z.sha256
```

### Disaster Recovery
Detailed recovery procedures are available in the [Backup System Documentation](./docs/memory-bank/operations/backup-system.md).

## 🌐 Remote Access

### Cloudflare Tunnel
Secure remote access without port forwarding:
- Zero-trust network access
- Automatic SSL/TLS encryption
- DDoS protection
- Geographic load balancing

### Configuration
1. Create Cloudflare Tunnel in dashboard
2. Configure tunnel token in environment file
3. Set up DNS records pointing to tunnel
4. Deploy tunnel service

## 🛠️ Troubleshooting

### Quick Diagnostics
```bash
# Check all services
docker compose ps

# View recent logs
docker compose logs --tail=50

# Test connectivity
curl -I http://localhost:8080
nslookup google.com localhost
```

### Common Issues
- **Port Conflicts**: Check for conflicting services on ports 80, 53, 8080
- **Permission Issues**: Verify data directory ownership and permissions
- **DNS Issues**: Ensure Pi-hole is properly configured as DNS server
- **Storage Issues**: Monitor disk space and backup storage

For detailed troubleshooting, see [Common Issues Guide](./docs/memory-bank/troubleshooting/common-issues.md).

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Test changes in isolated environment
4. Update documentation as needed
5. Submit pull request

### Guidelines
- Follow existing configuration patterns
- Include health checks for new services
- Update memory bank documentation
- Test backup and recovery procedures
- Maintain security best practices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 External Resources

### Official Documentation
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Nextcloud Documentation](https://docs.nextcloud.com/)
- [Pi-hole Documentation](https://docs.pi-hole.net/)
- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)

### Community Resources
- [Self-Hosted Subreddit](https://www.reddit.com/r/selfhosted/)
- [Awesome Self-Hosted](https://github.com/awesome-selfhosted/awesome-selfhosted)
- [Docker Hub](https://hub.docker.com/)

## 📞 Support

### Documentation
- Start with the [Memory Bank](./docs/memory-bank/README.md)
- Check [Common Issues](./docs/memory-bank/troubleshooting/common-issues.md)
- Review service-specific documentation

### Community Support
- GitHub Issues for bug reports and feature requests
- Discussions for questions and community support
- Wiki for additional documentation and guides

---

**⚠️ Important**: Always backup your data before making changes to the configuration. Test changes in a development environment when possible.

**🔐 Security Note**: Change all default passwords and regularly update your services for security patches.
