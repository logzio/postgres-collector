from os import environ
import yaml
import input_validator as iv


class Config:
    def __init__(self, configPath):
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
        # pg
        self.validatePg()
        if environ.get('PG_HOST') is None:
            environ['PG_HOST'] = self.pg['pg_host']
        if environ.get('PG_PORT') is None:
            environ['PG_PORT'] = str(self.pg['pg_port'])
        if environ.get('PG_USER') is None:
            environ['PG_USER'] = self.pg['pg_user']
        if environ.get('PG_PASSWORD') is None:
            environ['PG_PASSWORD'] = self.pg['pg_password']
        if environ.get('PG_DB') is None:
            environ['PG_DB'] = self.pg['pg_db']

    # Returns the listener url based on the region input
    def getListenerUrl(self) -> str:
        if self.otel['custom_listener'] != "":
            return self.otel['custom_listener']
        else:
            return "https://listener.logz.io:8053".replace("listener.", "listener{}.".format(self.getRegionCode(self.otel['logzio_region'])))

    @staticmethod
    def getRegionCode(region) -> str:
        if region != "us" and region != "":
            return "-{}".format(region)
        return ""

    def validatePg(self) -> None:
        if environ.get('PG_HOST') is None and self.pg['pg_host'] is None:
            raise ValueError('PG_HOST or pg.pg_host must be set')
        if environ.get('PG_PORT') is None and self.pg['pg_port'] is None:
            raise ValueError('PG_PORT or pg.pg_port must be set')
        if environ.get('PG_USER') is None and self.pg['pg_user'] is None:
            raise ValueError('PG_USER or pg.pg_user must be set')
        if environ.get('PG_PASSWORD') is None and self.pg['pg_password'] is None:
            raise ValueError('PG_PASSWORD or pg.pg_password must be set')
