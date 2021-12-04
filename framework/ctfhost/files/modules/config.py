import configparser
import os

# init configparser with given config file
config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__)) + '/../config/framework.ini')

# default
def get_flag_prefix():
    """
    Returns flag prefix.
    """
    return config['DEFAULT']['flag_prefix']

def get_flag_suffix():
    """
    Returns flag suffix.
    """
    return config['DEFAULT']['flag_suffix']

# database
def get_database_url():
    """
    Returns the database url.
    """
    return config['DATABASE']['url']

def get_database_user():
    """
    Returns database user.
    """
    return config['DATABASE']['user']

def get_database_password():
    """
    Returns database password.
    """
    return config['DATABASE']['password']

# basic auth
def get_basic_auth_username():
    """
    Returns basic auth username.
    """
    return config['BASIC_AUTH']['username']

def get_basic_auth_password():
    """
    Returns basic auth password.
    """
    return config['BASIC_AUTH']['password']

# logging
def get_logging_level():
    """
    Returns the logging level.
    """
    return config['LOGGING']['level']

def get_logging_logfile_name():
    """
    Returns the relative path from the base project path to the logging file.
    """
    return config['LOGGING']['logfile']