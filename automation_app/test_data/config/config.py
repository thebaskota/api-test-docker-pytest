import logging
from load_config import get_configs
from utilities.custom_logger import customlogger

Settings_Rest_api = {}
Settings_Graphql = {}
Settings_Common = {}

# Update local variables dynamically
locals().update(get_configs())

# Create a logger class
class SettingsUpdaterLogger:
    log = customlogger(logging.DEBUG)
