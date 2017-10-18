import configparser


class Config:
    config_parser = None

    @staticmethod
    def init_config():
        Config.config_parser = configparser.ConfigParser()
        Config.config_parser.read("res/config.ini")

    @staticmethod
    def get_config():
        if not Config.config_parser:
            Config.init_config()
        return Config.config_parser
