# common helper function
import os

from django.core.exceptions import ImproperlyConfigured


def get_option_value(option_tuple, key):
    '''
    This function will return the value of key when a tuple is optional in a model
    :param option_tuple: tuple of tuple
    :param key: value in zeroth index of tuple
    :return: value in first index of tuple
    '''
    for type in option_tuple:
        if type[0] == key:
            return type[1]
    return None


"""
Function: get_env_variable
CREDITS : https://gist.github.com/pydanny/6094883
"""


def get_env_variable(var_name):
    """
    Get environment variable with given key , to be used to fetch
    sensitive info in production
    :param var_name: key
    :return: value for key else raise exception
    """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)


def to_utf(string):
    if isinstance(string, str):
        return string
    elif isinstance(string, bytes):
        return string.decode('UTF-8')
    else:
        raise ValueError('Only string or byte encoded values are allowed.')
