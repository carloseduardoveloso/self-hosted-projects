#!/usr/bin/env bash
set -euo pipefail

# ===== Configuracao =====
SOURCE_DIR="/home/cadu/self-hosted-projects/nextcloud/data/nextcloud/data"
BACKUP_DIR="/mnt/data/backups/nextcloud-data"
RETENTION_DAYS=7

# Docker/Compose e Nextcloud
NEXTCLOUD_CONTAINER="nextcloud"
COMPOSE_DIR="/home/cadu/self-hosted-projects/nextcloud"
COMPOSE_BIN="docker compose"
COMPOSE_SERVICE="nextcloud"

# Log
LOG_DIR="/home/cadu/self-hosted-projects/backup/log"
LOG_FILE="${LOG_DIR}/backup-$(date +'%Y%m%d').log"
mkdir -p "$LOG_DIR"
# redireciona stdout/stderr para o arquivo e para a tela
exec > >(tee -a "$LOG_FILE") 2>&1

# Exclusoes (paths relativos a SOURCE_DIR)
EXCLUDES=(
  "appdata_*"
  "files_trashbin"
  "cache"
  "tmp"
  "temp"
  "sessions"
)

# ===== Util =====
log() { printf '[%s] %s\n' "$(date +'%F %T')" "$*" >&2; }

umask 027
mkdir -p "$BACKUP_DIR" /var/lock "$LOG_DIR"

timestamp="$(date +'%Y%m%d-%H%M%S')"
host="$(hostname -s)"
base="nextcloud-data_${host}_${timestamp}"
tmpdir="$(mktemp -d)"
lockfile="/var/lock/backup-nextcloud-data.lock"

OCC=(docker exec -u www-data "$NEXTCLOUD_CONTAINER" php -d apc.enable_cli=1 occ)

_MAINT_ON=0
_STOPPED=0

cleanup() {
  # Em erro/saida: garanta container iniciado e manutencao desligada
  if [[ "$_STOPPED" -eq 1 ]]; then
    (cd "$COMPOSE_DIR" && $COMPOSE_BIN start "$COMPOSE_SERVICE") || true
    _STOPPED=0
  fi
  if [[ "$_MAINT_ON" -eq 1 ]]; then
    (cd "$COMPOSE_DIR" && $COMPOSE_BIN start "$COMPOSE_SERVICE") || true
    "${OCC[@]}" maintenance:mode --off || true
    _MAINT_ON=0
  fi
  rm -rf "$tmpdir" || true
  rm -f "$lockfile" || true
}
trap cleanup EXIT

# Trava
exec 9>"$lockfile"
if ! flock -n 9; then
  log "Outro backup esta em andamento. Abortando."
  exit 1
fi

# Valida diretorio fonte
if [[ ! -d "$SOURCE_DIR" ]]; then
  log "Diretorio fonte inexistente: $SOURCE_DIR"
  exit 2
fi

# 7zip (7zz preferencial; fallback para 7z)
if command -v 7zz >/dev/null 2>&1; then
  SEVENZIP="7zz"
elif command -v 7z >/dev/null 2>&1; then
  SEVENZIP="7z"
else
  log "7zip nao encontrado. Instale com: sudo apt-get install -y 7zip  (ou p7zip-full)"
  exit 3
fi

ARCH_EXT="tar.7z"
archive="${BACKUP_DIR}/${base}.${ARCH_EXT}"
checksum="${archive}.sha256"

# Monta exclusoes p/ tar
tar_excludes=()
for e in "${EXCLUDES[@]}"; do
  tar_excludes+=(--exclude="${e}")
done

# 1) Ativa modo manutencao (precisa do container rodando)
log "Ativando modo de manutencao do Nextcloud..."
"${OCC[@]}" maintenance:mode --on
_MAINT_ON=1

# 2) Para o container antes do backup
log "Parando o container ${COMPOSE_SERVICE}..."
if (cd "$COMPOSE_DIR" && $COMPOSE_BIN stop "$COMPOSE_SERVICE"); then
  _STOPPED=1
else
  log "Aviso: nao foi possivel parar o container. Prosseguindo."
fi

# 3) Cria o arquivo de backup (tar -> 7z via stdin; preserva metadados POSIX no tar)
log "Gerando backup em ${archive} ..."
set +e
(
  cd "$SOURCE_DIR"
  tar -cpf - ${tar_excludes[@]+"${tar_excludes[@]}"} .
) | $SEVENZIP a -si"${base}.tar" "$archive" -mx=9 -mmt=on -bd -bso0 -bsp1
rc=${PIPESTATUS[1]}
set -e
if (( rc > 1 )); then
  log "Falha ao comprimir com 7zip (rc=$rc)."
  exit 4
fi

# 4) Checksum e validacao
sha256sum "$archive" > "$checksum"
sha256sum -c "$checksum" >/dev/null

# 5) Rotacao
find "$BACKUP_DIR" -type f -name "nextcloud-data_*.tar.7z"   -mtime +"$RETENTION_DAYS" -print -delete || true
find "$BACKUP_DIR" -type f -name "nextcloud-data_*.sha256"   -mtime +"$RETENTION_DAYS" -print -delete || true

# 6) Inicia container e desativa manutencao
if [[ "$_STOPPED" -eq 1 ]]; then
  log "Iniciando o container ${COMPOSE_SERVICE}..."
  (cd "$COMPOSE_DIR" && $COMPOSE_BIN start "$COMPOSE_SERVICE") || true
  _STOPPED=0
fi

# aguarda o container ficar Running
log "Aguardando o Nextcloud iniciar..."
for i in {1..30}; do
  if docker inspect -f '{{.State.Running}}' "$NEXTCLOUD_CONTAINER" 2>/dev/null | grep -q true; then
    break
  fi
  sleep 2
done

log "Desativando modo de manutencao do Nextcloud..."
"${OCC[@]}" maintenance:mode --off || true
_MAINT_ON=0

log "OK: backup em $archive"
log "Nextcloud reativado. Pode usar."
