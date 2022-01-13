import logging
import os
import random
import string
import time

from config import Config
import yaml
import socket
from contextlib import closing


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


class Builder:
    def __init__(self, configPath, otelConfigPath="./config_files/otel-config.yml") -> None:
        self.config = Config(configPath)
        self.logger = self.createLogger()
        self.otelConfigPath = otelConfigPath

    # Initialize logger
    def createLogger(self) -> logging.Logger:
        DEFAULT_LOG_LEVEL = "INFO"
        LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        try:
            user_level = self.config.otel['logzio_log_level'].upper()
            level = user_level if user_level in LOG_LEVELS else DEFAULT_LOG_LEVEL
        except KeyError:
            level = DEFAULT_LOG_LEVEL

        logging.basicConfig(format='%(asctime)s\t\t%(levelname)s\t[%(name)s]\t%(filename)s:%(lineno)d\t%(message)s',
                            level=level)
        return logging.getLogger(__name__)

    # Takes dict representation of of yaml and dump it to a yaml file
    @staticmethod
    def dumpAndCloseFile(moduleYaml, moduleFile) -> None:
        yaml.preserve_quotes = True
        moduleFile.seek(0)
        yaml.dump(moduleYaml, moduleFile)
        moduleFile.truncate()
        moduleFile.close()

    # Finds free port

    # Takes instance configuration and creates corresponding object for otel collector
    def createInstanceExporter(self, instance) -> dict:
        port = find_free_port()
        instanceObj = {
            'exec': './postgres_exporter',
            'scrape_interval': f"{self.config.pg['pg_scrape_interval']}s",
            'scrape_timeout': f"{self.config.pg['pg_scrape_timeout']}s",
            'port': port,
            'env': []
        }
        instanceObj['env'].append({
            "name": "DATA_SOURCE_NAME",
            "value": f"postgresql://{instance['pg_user']}:{instance['pg_password']}@{instance['pg_host']}:{instance['pg_port']}/{instance['pg_db']}"
        })
        instanceObj['env'].append({
            "name": "PG_EXPORTER_DISABLE_DEFAULT_METRICS",
            "value": "true"
        })
        instanceObj['env'].append({
            "name": "PG_EXPORTER_WEB_LISTEN_ADDRESS",
            "value": f":{port}"
        })
        instanceObj['env'].append({
            "name": "PG_EXPORTER_EXTEND_QUERY_MR_PATH",
            "value": "queries/"
        })
        instanceObj['env'].append({
            "name": "PG_EXPORTER_EXTEND_QUERY_MR",
            "value": "true"
        })
        # generate label string
        try:
            labelsString = ''
            for label in instance['pg_labels']:
                for k, v in label.items():
                    labelsString = f'{labelsString},{k}={v}'

            instanceObj['env'].append({
                "name": "PG_EXPORTER_CONSTANT_LABELS",
                "value": labelsString[1:]
            })
        except KeyError:
            return instanceObj

        return instanceObj

    # Takes user input and applies it to open telemetry collector
    def updateOtelConfiguration(self) -> None:
        self.logger.info('Adding opentelemtry collector configuration')
        with open(self.otelConfigPath, 'r+') as otelFile:
            values = yaml.safe_load(otelFile)
            # update pg
            for instance in self.config.pg['instances']:
                letters = string.ascii_lowercase
                identifier = ''.join(random.choice(letters) for i in range(5))
                values['receivers'][f'prometheus_exec/postgres-{instance["pg_host"]}-{identifier}'] = self.createInstanceExporter(instance)
                values['service']['pipelines']['metrics']['receivers'].append(f'prometheus_exec/postgres-{instance["pg_host"]}-{identifier}')
            # Update exporter
            values['exporters']['prometheusremotewrite']['endpoint'] = self.config.getListenerUrl()
            values['exporters']['prometheusremotewrite']['timeout'] = f"{self.config.otel['remote_timeout']}s"
            values['exporters']['prometheusremotewrite']['headers'][
                'Authorization'] = f"Bearer {self.config.otel['token']}"
            values['exporters']['prometheusremotewrite']['external_labels']['p8s_logzio_name'] = self.config.otel[
                'p8s_logzio_name']
            # Update service
            values['service']['telemetry']['logs']['level'] = self.config.otel['log_level']
            self.dumpAndCloseFile(values, otelFile)
        self.logger.info('Opentelemtry collector configuration ready')
        self.logger.debug(f'Opentelemtry collector configuration:\n{yaml.dump(values)}')


if __name__ == '__main__':
    builder = Builder('./config_files/config.yml')
    builder.updateOtelConfiguration()
    time.sleep(2.0)
    os.system('/otelcontribcol_linux_amd64 --config ./config_files/otel-config.yml')
