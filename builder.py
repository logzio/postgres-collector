import logging
import os
import time

from config import Config
import yaml


class Builder:
    def __init__(self, configPath, otelConfigPath="./config_files/otel-config.yml",
                 cloudwatchConfigPath="./config_files/cloudwatch.yml") -> None:
        self.config = Config(configPath)
        self.logger = self.createLogger()
        self.otelConfigPath = otelConfigPath
        self.cloudwatchConfigPath = cloudwatchConfigPath

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

    # Takes user input and applies it to open telemetry collector
    def updateOtelConfiguration(self) -> None:
        self.logger.info('Adding opentelemtry collector configuration')
        with open(self.otelConfigPath, 'r+') as otelFile:
            values = yaml.safe_load(otelFile)
            # update pg
            values['receivers']['prometheus_exec/postgres']['scrape_interval'] = f"{self.config.pg['pg_scrape_interval']}s"
            values['receivers']['prometheus_exec/postgres']['scrape_timeout'] = f"{self.config.pg['pg_scrape_timeout']}s"
            values['receivers']['prometheus_exec/postgres']['env'].append(
                {
                    "name": "DATA_SOURCE_NAME",
                    "value": f"postgresql://{os.environ['PG_USER']}:{os.environ['PG_PASSWORD']}@{os.environ['PG_HOST']}:{os.environ['PG_PORT']}/{os.environ['PG_DB']}"
                }
            )

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

