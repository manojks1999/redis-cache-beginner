# import timedelta
from datetime import timedelta, datetime
import os
# import config
import api.config as config

# import flask
from flask import Flask, has_request_context, request as req

# import cors
# from flask_cors import CORS

# db
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

# import db conn. retrying class
from api.db import RetryingQuery

from redis import Redis

# global db objects
engine = None
db_session = None

def create_app(environment):
    """
    Initialize flask WSGI application with a config object.

    params:
        - config_object: flask configuration object (class)
    """
    try:
        config_object = config.Config
        # create Flask object
        app = Flask(__name__, instance_relative_config=False)
        # create Flask object
        app = Flask(__name__, instance_relative_config=False)
        
        global engine
        engine = create_engine(
            os.environ.get("DEVELOPMENT_SQLALCHEMY_DATABASE_URI"),
            echo=False,
        )
        # intialize database session (verbose SQL operations can be activated here)
        Session = scoped_session(sessionmaker(bind=engine))
        # get session
        global db_session
        # create session
        db_session = Session()
        db_session.connection(
            execution_options={
                "schema_translate_map": {"development": "development"}
            }
        )
        global redis_cache
        redis_cache = Redis(
            host = config_object.REDIS_HOST,
            port = config_object.REDIS_PORT,
            password = config_object.REDIS_PASSWORD
        )
        # get declarative base
        global Base
        # initialize declarative base
        Base = declarative_base()
        from .schema import DeviceLocations
        # bind engine with declarative base
        Base.metadata.bind = engine
        # Base.metadata.create_all(engine)
        # pass application context
        with app.app_context():
            # import blueprints
            from api.api import apis_blueprint
            app.register_blueprint(apis_blueprint)
            return app
    except Exception as e:
        print("error", e)
        return None