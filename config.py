import json
import logging
from os import environ
import yaml
import input_validator as iv


class Config:
    def __init__(self, configPath):
        self.logger = self.createLogger()
        # Try to load from config file
        with open(configPath) as f:
            dataMap = yaml.safe_load(f)
            self.__dict__.update(**dataMap)
        # Try to load from env variables
        # Open telemetry:
        if environ.get('LOGZIO_REGION') is not None:
            self.otel['logzio_region'] = environ.get('LOGZIO_REGION')
        if environ.get('TOKEN') is not None:
            self.otel['token'] = environ.get('TOKEN')
        if environ.get('P8S_LOGZIO_NAME') is not None:
            self.otel['p8s_logzio_name'] = environ.get('P8S_LOGZIO_NAME')
        if environ.get('CUSTOM_LISTENER') is not None:
            self.otel['custom_listener'] = environ.get('CUSTOM_LISTENER')
        if environ.get('REMOTE_TIMEOUT') is not None:
            self.otel['remote_timeout'] = int(environ.get('REMOTE_TIMEOUT'))
        if environ.get('LOG_LEVEL') is not None:
            self.otel['log_level'] = environ.get('LOG_LEVEL')
        if environ.get('LOGZIO_LOG_LEVEL') is not None:
            self.otel['logzio_log_level'] = environ.get('LOGZIO_LOG_LEVEL')

        # Pg exporter
        if environ.get('PG_SCRAPE_INTERVAL') is not None:
            self.pg['pg_scrape_interval'] = environ.get('PG_SCRAPE_INTERVAL')
        if environ.get('PG_SCRAPE_TIMEOUT') is not None:
            self.pg['pg_scrape_timeout'] = environ.get('PG_SCRAPE_TIMEOUT')
        if environ.get('PG_INSTANCES') is not None:
            try:
                instances = []
                instancesRaw = environ.get('PG_INSTANCES').split(',')
                for instance in instancesRaw:
                    json.loads(instance)
                    validatedInstance = self.validatePgInstance(instance)
                    if validatedInstance is not None:
                        instances.append(validatedInstance)
            except Exception as e:
                raise Exception(f"Failed to parse PG_INSTANCES string: {e}")
            self.pg['pg_scrape_interval'] = instances

    # Returns the listener url based on the region input
    def getListenerUrl(self) -> str:
        if self.otel['custom_listener'] != "":
            return self.otel['custom_listener']
        else:
            return "https://listener.logz.io:8053".replace("listener.", "listener{}.".format(
                self.getRegionCode(self.otel['logzio_region'])))

    @staticmethod
    def getRegionCode(region) -> str:
        if region != "us" and region != "":
            return "-{}".format(region)
        return ""

    def validatePgInstance(self, instance) -> dict:
        try:
            if instance['pg_host'] is None:
                raise ValueError('pg_host must be set')
            if instance['pg_port'] is None:
                raise ValueError('pg_port must be set')
            if instance['pg_user'] is None:
                raise ValueError('pg_user must be set')
            if instance['pg_password'] is None:
                raise ValueError('pg_password must be set')
        except Exception as e:
            self.logger.warning(f'Failed to parse, dropping instance: {json.dumps(instance)}\n Error message: {e}')
            return None

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
