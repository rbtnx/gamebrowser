class Config(object):
    APP_NAME = "Gamebrowser"
    STATIC_FOLDER = 'static'
    DEBUG = True
    DEVELOPMENT = False
    TESTING = False
    STAGING = False
    PRODUCTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEVELOPMENT = True

class TestingConfig(Config):
    TESTING = True

class StagingConfig(Config):
    STAGING = True

class ProductionConfig(Config):
    PRODUCTION = True
    DEBUG = False
