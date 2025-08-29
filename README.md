# Pi-hole + Unbound Docker Setup

A complete DNS solution combining Pi-hole for ad-blocking and DNS filtering with Unbound as a recursive DNS resolver for enhanced privacy and performance.

## 🚀 Features

- **Pi-hole**: Network-wide ad blocking and DNS filtering
- **Unbound**: Recursive DNS resolver for enhanced privacy
- **Watchtower**: Automatic container updates
- **Health Checks**: Built-in monitoring for all services
- **Security**: Hardened container configurations
- **Performance**: Optimized caching and threading
- **Privacy**: DNSSEC validation and private DNS resolution

## 📋 Prerequisites

- Docker and Docker Compose installed
- Ports 53, 80, 443 available on the host
- At least 1GB RAM recommended
- Static IP address for the host (recommended)

## 🛠️ Installation

1. **Clone or download this configuration**
   ```bash
   git clone <repository-url>
   cd pihole-unbound
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   nano .env
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Verify services are running**
   ```bash
   docker-compose ps
   docker-compose logs
   ```

## ⚙️ Configuration

### Environment Variables (.env file)

```bash
# Timezone (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
TZ=America/Sao_Paulo

# Pi-hole Configuration
PIHOLE_PASSWORD=your_secure_password_here
PIHOLE_HOSTNAME=pihole.local

# Unbound Performance Tuning
UNBOUND_THREADS=2
UNBOUND_CACHE_SIZE=256m
UNBOUND_VERBOSITY=1
```

### Pi-hole Configuration

- **Web Interface**: http://your-server-ip or https://your-server-ip
- **Default Password**: Set via `PIHOLE_PASSWORD` environment variable
- **DNS Settings**: Automatically configured to use Unbound
- **DNSSEC**: Enabled by default for enhanced security

### Unbound Configuration

- **Custom Config**: Place configuration files in `./unbound-config/`
- **Logs**: Available in `./unbound-logs/`
- **Performance**: Configurable via environment variables
- **Security**: Runs with read-only filesystem and no new privileges

## 🔧 Advanced Configuration

### Custom Unbound Configuration

Create custom configuration files in the `unbound-config` directory:

```bash
mkdir -p unbound-config
```

Example `unbound-config/unbound.conf`:
```
server:
    # Performance
    num-threads: 2
    msg-cache-size: 128m
    rrset-cache-size: 256m
    cache-max-ttl: 86400
    
    # Privacy
    hide-identity: yes
    hide-version: yes
    
    # Security
    harden-glue: yes
    harden-dnssec-stripped: yes
    use-caps-for-id: yes
    
    # Access control
    access-control: 172.20.0.0/16 allow
    access-control: 127.0.0.0/8 allow
```

### Pi-hole Custom Lists

Add custom blocklists or whitelists through the Pi-hole web interface or by placing files in:
- `./etc-pihole/` - Pi-hole configuration and databases
- `./etc-dnsmasq.d/` - Custom dnsmasq configuration

## 🌐 Network Configuration

The setup uses a custom Docker network with static IP addresses:
- **Network**: 172.20.0.0/16
- **Pi-hole**: 172.20.0.5
- **Unbound**: 172.20.0.6

### Router Configuration

To use this DNS setup network-wide:

1. **Set your router's DNS servers to your Docker host IP**
2. **Or configure individual devices to use your Docker host IP as DNS**
3. **For DHCP**: Optionally enable Pi-hole's DHCP server (uncomment port 67 in docker-compose.yml)

## 📊 Monitoring and Logs

### Health Checks

All services include health checks:
- **Pi-hole**: Tests DNS resolution
- **Unbound**: Tests recursive DNS queries
- **Watchtower**: Monitors for updates

### Logs

Access logs using Docker Compose:
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs pihole
docker-compose logs unbound

# Follow logs in real-time
docker-compose logs -f
```

### Log Files

- **Pi-hole logs**: `./var-log/`
- **Unbound logs**: `./unbound-logs/`

## 🔄 Updates

Watchtower automatically updates containers daily. To manually update:

```bash
# Pull latest images
docker-compose pull

# Recreate containers with new images
docker-compose up -d
```

## 🛡️ Security Features

- **Read-only containers**: Unbound runs with read-only filesystem
- **No new privileges**: Security hardening enabled
- **Network isolation**: Custom network with controlled access
- **DNSSEC validation**: Enabled for DNS security
- **Privacy mode**: Pi-hole configured for maximum privacy

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 53, 80, 443 are not in use
   ```bash
   sudo netstat -tulpn | grep :53
   sudo netstat -tulpn | grep :80
   ```

2. **DNS not working**: Check if services are healthy
   ```bash
   docker-compose ps
   docker-compose logs unbound
   ```

3. **Pi-hole not accessible**: Verify firewall settings
   ```bash
   sudo ufw status
   ```

### Testing DNS Resolution

```bash
# Test Pi-hole
dig @your-server-ip google.com

# Test Unbound directly
dig @your-server-ip -p 5053 google.com

# Test DNSSEC
dig @your-server-ip cloudflare.com +dnssec
```

### Reset Configuration

To start fresh:
```bash
docker-compose down
sudo rm -rf etc-pihole/ etc-dnsmasq.d/ var-log/ unbound-config/ unbound-logs/
docker-compose up -d
```

## 📁 Directory Structure

```
pihole-unbound/
├── docker-compose.yml      # Main configuration
├── .env                   # Environment variables
├── README.md              # This file
├── etc-pihole/           # Pi-hole data (auto-created)
├── etc-dnsmasq.d/        # Custom dnsmasq config (auto-created)
├── var-log/              # Pi-hole logs (auto-created)
├── unbound-config/       # Unbound configuration (auto-created)
└── unbound-logs/         # Unbound logs (auto-created)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 References

- [Pi-hole Documentation](https://docs.pi-hole.net/)
- [Unbound Documentation](https://unbound.docs.nlnetlabs.nl/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Pi-hole Docker Hub](https://hub.docker.com/r/pihole/pihole)
- [Unbound Docker Hub](https://hub.docker.com/r/mvance/unbound)

## ⚠️ Important Notes

- **Backup regularly**: Your Pi-hole configuration and blocklists
- **Monitor resources**: Ensure adequate RAM and storage
- **Update regularly**: Keep containers updated for security
- **Test changes**: Always test configuration changes in a safe environment
- **Network impact**: Changes affect all devices using this DNS server
