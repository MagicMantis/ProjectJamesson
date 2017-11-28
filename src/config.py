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
        dates = []
        with open(os.path.dirname(os.path.realpath(__file__))+'/../res/training_dates.txt', 'r') as dates_file:
            dates = [Config.parse_date(ds) for ds in dates_file.readlines()]
        return dates

    @staticmethod
    def parse_date(date_string):
        return date(int(date_string.split('/')[2]), int(date_string.split('/')[0]), int(date_string.split('/')[1]))

