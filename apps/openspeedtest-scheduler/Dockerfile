# Dockerfile para o scheduler que usa Ookla Speedtest CLI + Python
FROM python:3.12-slim

# Instala speedtest (repo oficial Ookla) e utilitarios
RUN apt-get update && apt-get install -y curl gnupg ca-certificates && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /etc/apt/keyrings \
 && curl -fsSL https://packagecloud.io/ookla/speedtest-cli/gpgkey | gpg --dearmor -o /etc/apt/keyrings/ookla.gpg \
 && echo "deb [signed-by=/etc/apt/keyrings/ookla.gpg] https://packagecloud.io/ookla/speedtest-cli/debian/ bookworm main" > /etc/apt/sources.list.d/ookla.list \
 && apt-get update && apt-get install -y speedtest && rm -rf /var/lib/apt/lists/*

# Dependencias Python
RUN pip install --no-cache-dir schedule mysql-connector-python

# Cria usuario nao-root
RUN useradd -m -u 10001 appuser
WORKDIR /app
COPY scheduler.py /app/scheduler.py
RUN chown -R appuser:appuser /app
USER appuser

# Healthcheck simples: binario presente
HEALTHCHECK --interval=1m --timeout=10s --retries=3 \
  CMD speedtest -h >/dev/null 2>&1 || exit 1

CMD ["python", "/app/scheduler.py"]
