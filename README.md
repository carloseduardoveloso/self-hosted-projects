# Self-Hosted Projects

Uma coleção de soluções self-hosted prontas para uso com Docker Compose. Este repositório contém configurações testadas e documentadas para diversas aplicações que você pode hospedar em sua própria infraestrutura.

## 🚀 Aplicações Disponíveis
### 🛡️ [Pi-hole](./pihole/)
Bloqueador de anúncios e DNS sinkhole para toda a rede.
- **Portas**: 53 (DNS), 80 (HTTP), 443 (HTTPS)
- **Características**: Bloqueio de anúncios, DNS personalizado, dashboard web

### 💻 [Code Server](./codeserver/)
VS Code executando no navegador para desenvolvimento remoto.
- **Características**: IDE completo no navegador, extensões, terminal integrado

### ☁️ [Nextcloud](./nextcloud/)
Plataforma de colaboração e armazenamento em nuvem.
- **Características**: Sincronização de arquivos, calendário, contatos, office online

## 📋 Pré-requisitos

- **Docker** (versão 20.10 ou superior)
- **Docker Compose** (versão 2.0 ou superior)
- **Sistema operacional**: Linux, macOS ou Windows com WSL2

### Instalação do Docker

#### Ubuntu/Debian
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### CentOS/RHEL
```bash
sudo yum install -y docker docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

## 🛠️ Instalação Rápida

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/carloseduardoveloso/self-hosted-projects.git
   cd self-hosted-projects
   ```

2. **Escolha uma aplicação**:
   ```bash
   cd <nome-da-aplicacao>  # ex: cd memorybank
   ```

3. **Configure as variáveis de ambiente**:
   ```bash
   cp .env.example .env
   nano .env  # Edite conforme necessário
   ```

4. **Inicie a aplicação**:
   ```bash
   docker-compose up -d
   ```

## 📁 Estrutura do Projeto

```
self-hosted-projects/
├── README.md                 # Este arquivo
├── LICENSE                   # Licença do projeto
├── .gitignore               # Arquivos ignorados pelo Git
├── memorybank/              # Sistema de conhecimento pessoal
│   ├── docker-compose.yml
│   ├── .env.example
│   └── README.md
├── pihole/                  # Bloqueador de anúncios DNS
│   ├── docker-compose.yml
│   ├── .env
│   └── README.md
├── codeserver/              # VS Code no navegador
│   ├── docker-compose.yml
│   └── README.md
└── nextcloud/               # Plataforma de nuvem pessoal
    ├── docker-compose.yml
    └── README.md
```

## 🔧 Comandos Úteis

### Gerenciamento Geral
```bash
# Ver status de todos os containers
docker ps

# Ver logs de um container específico
docker-compose logs -f <service-name>

# Parar todos os containers
docker stop $(docker ps -q)

# Remover containers parados
docker container prune

# Remover imagens não utilizadas
docker image prune
```

### Backup e Restauração
```bash
# Backup de volumes Docker
docker run --rm -v <volume-name>:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /data .

# Restaurar backup
docker run --rm -v <volume-name>:/data -v $(pwd):/backup alpine tar xzf /backup/backup.tar.gz -C /data
```

## 🔒 Segurança

### Recomendações Gerais
- ✅ Sempre altere senhas padrão
- ✅ Use HTTPS em produção (configure um proxy reverso)
- ✅ Mantenha backups regulares
- ✅ Atualize as imagens Docker regularmente
- ✅ Configure firewall adequadamente
- ✅ Use redes Docker isoladas quando possível

### Proxy Reverso (Recomendado)
Para produção, recomenda-se usar um proxy reverso como:
- **Traefik** (automático com Docker labels)
- **Nginx Proxy Manager** (interface web)
- **Caddy** (HTTPS automático)

## 🔄 Atualizações

Para atualizar uma aplicação:

```bash
cd <nome-da-aplicacao>
docker-compose down
docker-compose pull
docker-compose up -d
```

## 🐛 Troubleshooting

### Problemas Comuns

1. **Porta já em uso**:
   ```bash
   # Verificar qual processo está usando a porta
   sudo netstat -tulpn | grep :80
   # Ou alterar a porta no docker-compose.yml
   ```

2. **Permissões de arquivo**:
   ```bash
   sudo chown -R $USER:$USER ./data
   ```

3. **Espaço em disco insuficiente**:
   ```bash
   # Limpar containers e imagens não utilizadas
   docker system prune -a
   ```

4. **Container não inicia**:
   ```bash
   # Verificar logs detalhados
   docker-compose logs <service-name>
   ```

## 🤝 Contribuindo

Contribuições são bem-vindas! Para adicionar uma nova aplicação:

1. Fork este repositório
2. Crie uma pasta para a nova aplicação
3. Adicione `docker-compose.yml`, `.env.example` e `README.md`
4. Atualize este README principal
5. Envie um Pull Request

### Padrões para Contribuições
- Use comentários descritivos nos arquivos YAML
- Inclua healthchecks quando possível
- Configure volumes para persistência de dados
- Documente todas as variáveis de ambiente
- Teste a configuração antes de enviar

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## 🔗 Links Úteis

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Awesome Self-Hosted](https://github.com/awesome-selfhosted/awesome-selfhosted)
- [r/selfhosted](https://www.reddit.com/r/selfhosted/)

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/carloseduardoveloso/self-hosted-projects/issues)
- **Discussões**: [GitHub Discussions](https://github.com/carloseduardoveloso/self-hosted-projects/discussions)

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!
