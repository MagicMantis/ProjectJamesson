import configparser
import os
from datetime import date

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

    @staticmethod
    def parse_training_dates():
        dates = None
        with open('/../res/training_dates.txt') as dates_file:
            dates = dates_file.read_lines()

    @staticmethod
    def 
