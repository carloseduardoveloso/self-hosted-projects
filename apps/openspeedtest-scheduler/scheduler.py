#!/usr/bin/env python3
"""
OpenSpeedTest Scheduler (via Ookla Speedtest CLI)
Executa testes de velocidade periodicamente (default: 15 minutos) e salva no MariaDB.
"""

import os
import time
import json as pyjson
import logging
import schedule
import subprocess
import mysql.connector
from datetime import datetime
from typing import Dict, Any, Optional

# Logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SpeedTestScheduler:
    def __init__(self):
        # Intervalo de execucao (minutos), default 15
        self.interval_minutes = int(os.getenv("SCHEDULE_EVERY_MINUTES", "15"))

        # Config DB
        self.db_config = {
            "host": os.getenv("MYSQL_HOST", "host.docker.internal"),
            "port": int(os.getenv("MYSQL_PORT", "3306")),
            "database": os.getenv("OPENSPEEDTEST_DB_NAME", "openspeedtest"),
            "user": os.getenv("OPENSPEEDTEST_DB_USER", "openspeedtest_user"),
            "password": os.getenv("OPENSPEEDTEST_DB_PASSWORD", "OpenSpeedTest123"),
        }

        self.init_database()

    # ----------------------
    # Infra: Banco de dados
    # ----------------------
    def init_database(self) -> None:
        """Cria tabela se nao existir"""
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS speedtest_results (
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
            )
            """
            cursor.execute(create_table_query)
            conn.commit()
            logger.info("Database table initialized successfully")
        except mysql.connector.Error as e:
            logger.error(f"Database initialization error: {e}")
        finally:
            try:
                if cursor:
                    cursor.close()
                if conn and conn.is_connected():
                    conn.close()
            except Exception:
                pass

    # ----------------------
    # Execucao do teste
    # ----------------------
    @staticmethod
    def _bps_to_mbps(bytes_per_second: float) -> float:
        # bytes/s -> Mb/s
        return round((bytes_per_second * 8) / 1_000_000.0, 2)

    def run_speed_test(self) -> Optional[Dict[str, Any]]:
        """
        Executa o teste via 'speedtest' (Ookla) e retorna dict normalizado.
        Requer o binario 'speedtest' no PATH do container.
        """
        try:
            logger.info("Starting speed test (Ookla CLI)...")
            raw = subprocess.check_output(
                ["speedtest", "--accept-license", "--accept-gdpr", "--format=json"],
                timeout=300
            ).decode("utf-8")

            data = pyjson.loads(raw)

            # Campos principais (ver JSON da Ookla)
            # bandwidth: media em bytes/s
            dl_bps = float(data.get("download", {}).get("bandwidth", 0.0))
            ul_bps = float(data.get("upload", {}).get("bandwidth", 0.0))
            ping_ms = float(data.get("ping", {}).get("latency", 0.0))
            jitter_ms = float(data.get("ping", {}).get("jitter", 0.0))

            # Servidor e cliente
            server_obj = data.get("server", {}) or {}
            server = {
                "id": server_obj.get("id"),
                "name": server_obj.get("name"),
                "location": server_obj.get("location"),
                "country": server_obj.get("country"),
                "host": server_obj.get("host"),
                "ip": server_obj.get("ip"),
                "port": server_obj.get("port"),
            }
            client_ip = (data.get("interface", {}) or {}).get("externalIp", "")

            # Duracao: somatorio de elapsed de download e upload (ms) -> seg
            dl_elapsed_ms = int((data.get("download", {}) or {}).get("elapsed", 0))
            ul_elapsed_ms = int((data.get("upload", {}) or {}).get("elapsed", 0))
            duration_sec = int(round((dl_elapsed_ms + ul_elapsed_ms) / 1000.0))

            # Normaliza em Mbps
            result = {
                "download": self._bps_to_mbps(dl_bps),
                "upload": self._bps_to_mbps(ul_bps),
                "ping": round(ping_ms, 2),
                "jitter": round(jitter_ms, 2),
                "server": server,
                "client_ip": client_ip,
                "user_agent": "ookla-speedtest-cli",
                "duration": duration_sec,
            }

            logger.info(
                f"Speed test done - Down: {result['download']} Mbps, Up: {result['upload']} Mbps, Ping: {result['ping']} ms"
            )
            return result

        except subprocess.CalledProcessError as e:
            logger.error(f"Speedtest CLI failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during speed test: {e}")
            return None

    # ----------------------
    # Persistencia
    # ----------------------
    def save_results_to_db(self, results: Dict[str, Any]) -> None:
        """Salva o resultado no MariaDB"""
        if not results:
            logger.warning("No results to save")
            return

        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()

            insert_query = """
            INSERT INTO speedtest_results 
            (test_date, download_speed, upload_speed, ping_latency, jitter, 
             server_info, client_ip, user_agent, test_duration)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                datetime.now(),
                results.get("download", 0.0),
                results.get("upload", 0.0),
                results.get("ping", 0.0),
                results.get("jitter", 0.0),
                pyjson.dumps(results.get("server", {})),
                results.get("client_ip", ""),
                results.get("user_agent", ""),
                int(results.get("duration", 0)),
            )

            cursor.execute(insert_query, values)
            conn.commit()
            logger.info("Results saved to database")

        except mysql.connector.Error as e:
            logger.error(f"Database save error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving to database: {e}")
        finally:
            try:
                if cursor:
                    cursor.close()
                if conn and conn.is_connected():
                    conn.close()
            except Exception:
                pass

    # ----------------------
    # Orquestracao
    # ----------------------
    def execute_scheduled_test(self) -> None:
        """Executa o teste e persiste"""
        logger.info("Executing scheduled speed test...")
        result = self.run_speed_test()
        if result:
            self.save_results_to_db(result)
        else:
            logger.error("Failed to get speed test results")

    def start_scheduler(self) -> None:
        """Inicia agendador"""
        logger.info("Starting OpenSpeedTest Scheduler (Ookla CLI)...")
        logger.info(f"Speed tests will run every {self.interval_minutes} minutes")

        # Agenda
        schedule.every(self.interval_minutes).minutes.do(self.execute_scheduled_test)

        # Execucao inicial
        logger.info("Running initial speed test...")
        self.execute_scheduled_test()

        # Loop principal
        while True:
            schedule.run_pending()
            time.sleep(60)


def main() -> None:
    try:
        scheduler = SpeedTestScheduler()
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")


if __name__ == "__main__":
    main()
