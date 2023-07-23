# import environment manager
from dotenv import load_dotenv

# os to load environment variables
import os

# load environment variables
load_dotenv()


class Config():
    # db configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENVIRONMENT = os.environ.get("ENVIRONMENT")
    # debug mode
    DEBUG = True
    TESTING = False
    SQLALCHEMY_VERBOSE = True
    # local db
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEVELOPMENT_SQLALCHEMY_DATABASE_URI")
    REDIS_HOST = os.environ.get("REDIS_HOST")
    REDIS_PORT = os.environ.get("REDIS_PORT")
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")


class TestingConfig(Config):
    # debug mode
    DEBUG = True
    TESTING = True
    SQLALCHEMY_VERBOSE = True
    # local db
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEVELOPMENT_SQLALCHEMY_DATABASE_URI")


class DevelopmentConfig(Config):
    # production mode
    DEBUG = True
    TESTING = False
    SQLALCHEMY_VERBOSE = False
    # remote db
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEVELOPMENT_SQLALCHEMY_DATABASE_URI")


class ProductionConfig(Config):
    # production mode
    DEBUG = False
    TESTING = False
    SQLALCHEMY_VERBOSE = False
    # remote db
    SQLALCHEMY_DATABASE_URI = os.environ.get("PRODUCTION_SQLALCHEMY_DATABASE_URI")
