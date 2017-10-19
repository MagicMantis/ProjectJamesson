import configparser
import os

class Config:
    config_parser = None
    debug_mode = False

    @staticmethod
    def init_config():
        config_file_loc = os.path.dirname(os.path.realpath(__file__))+"/../res/config.ini"
        Config.config_parser = configparser.ConfigParser()
        Config.config_parser.read(config_file_loc)
        Config.debug_mode = Config.config_parser['DEFAULT'].getboolean('debug')

    @staticmethod
    def get_config():
        if not Config.config_parser:
            Config.init_config()
        return Config.config_parser

    @staticmethod
    def is_debug_mode():
        return Config.debug_mode
