"""
This module is for validating user's input
"""
import re
from testdata.data import aws_namespaces, aws_regions


# is_valid_logzio_token checks if a given token is a valid logz.io token
def is_valid_logzio_token(token):
    if type(token) is not str:
        raise TypeError("Token should be a string")
    regex = r"\b[a-zA-Z]{32}\b"
    match_obj = re.search(regex, token)
    if match_obj is not None and match_obj.group() is not None:
        if any(char.islower() for char in token) and any(char.isupper() for char in token):
            return True
    raise ValueError("Invalid token: {}".format(token))


# is_valid_logzio_region_code checks that a the region code is a valid logzio region code.
# an empty string ("") is also acceptable
def is_valid_logzio_region_code(logzio_region_code):
    if logzio_region_code is None or type(logzio_region_code) is not str:
        raise TypeError("Logzio region code should be a string")
    valid_logzio_regions = ["au", "ca", "eu", "nl", "uk", "us", "wa"]
    if logzio_region_code != "":
        if logzio_region_code not in valid_logzio_regions:
            raise ValueError("invalid logzio region code: {}. cannot start monitoring".format(logzio_region_code))
    return True


def is_valid_logz_io_modules(modules, suported_modules):
    if modules is None or type(modules) is not str:
        raise TypeError("Logzio modules parameter should be a string")
    logz_io_modules = modules.replace(' ', '').split(',')
    for module in logz_io_modules:
        if module not in suported_modules:
            raise ValueError(f'{module} module is not supported')
    return logz_io_modules


def is_valid_interval(interval):
    if interval is None or type(interval) is not int:
        raise TypeError("Parameter should be an integer")
    if (interval % 60) != 0 or interval <= 0:
        raise ValueError('Parameter should be in multiplies of 60')


def is_valid_aws_region(aws_region):
    if aws_region is None or type(aws_region) is not str:
        raise TypeError("AWS region parameter should be a string")
    if aws_region not in aws_regions:
        raise ValueError(f'{aws_region} is not supported')

def is_valid_rds_instances(instances):
    if type(instances) is str:
        rds_instances_list = instances.replace(' ', '').split(',')
    elif type(instances) is list:
        rds_instances_list = instances

    if rds_instances_list == ['']:
        raise ValueError('Cant find rds instances')
    return list(dict.fromkeys(rds_instances_list))




def is_valid_p8s_logzio_name(p8s):
    if type(p8s) is not str:
        raise TypeError("P8S_LOGZIO_NAME should be a string")


def is_valid_custom_listener(listener):
    if type(listener) is not str:
        raise TypeError("Custom listener should be a string")
    regex = r'^(http|https):\/\/(([a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])\.)*([a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])(:[0-9]+)?$'
    match_obj = re.search(regex, listener)
    if match_obj is not None and match_obj.group() is not None:
        return True
    else:
        raise ValueError("Invalid custom listener: {}".format(listener))
