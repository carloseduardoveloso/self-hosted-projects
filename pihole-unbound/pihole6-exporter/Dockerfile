FROM python:3.12-alpine
RUN pip install --no-cache-dir prometheus-client requests
ADD https://raw.githubusercontent.com/bazmonk/pihole6_exporter/main/pihole6_exporter /tmp/pihole6_exporter
RUN sed -i 's|https://{self.host}/api|http://{self.host}:80/api|g' /tmp/pihole6_exporter && \
    install -m 0755 /tmp/pihole6_exporter /usr/local/bin/pihole6_exporter
EXPOSE 9666
CMD ["pihole6_exporter","-H","pihole"]
