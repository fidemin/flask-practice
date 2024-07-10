import json
import logging
import os
import uuid
from json import JSONDecodeError
from logging.config import dictConfig

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask, request
from flask_apispec import FlaskApiSpec
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from src.main.common.celery_util import celery_init_app
from src.main.common.logging_util import default_logging_config

logger = logging.getLogger(__name__)


def logging_from_json(filepath: str):
    with open(filepath, 'r') as f:
        logging_config = json.load(f)
    return logging_config


naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))


def _generate_request_id():
    return str(uuid.uuid4())


from src.main.model import *  # noqa


def setup_config_for_db(app):
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    # app.config['SQLALCHEMY_ECHO'] = True


def create_app():
    if logging_filepath := os.getenv('LOGGING_CONFIG_FILE'):
        dictConfig(logging_from_json(logging_filepath))
    else:
        dictConfig(default_logging_config)

    app = Flask(__name__, static_folder='static')

    # app.config['SQLALCHEMY_ECHO'] = True

    setup_config_for_db(app)
    db.init_app(app)
    migrate = Migrate(app, db)

    # setting for celery
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = os.getenv('REDIS_PORT', '6379')
    app.config.from_mapping(
        CELERY=dict(
            broker_url=f"redis://{redis_host}:{redis_port}",
            result_backend=f"redis://{redis_host}:{redis_port}",
            task_ignore_result=True,
        ),
    )
    celery_init_app(app)

    from src.main.controller import api_bp
    from src.main.views import apispec_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(apispec_bp, url_prefix='/apispec')

    docs = FlaskApiSpec(app)
    docs.register_existing_resources()

    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='flask practice',
            version='v1',
            openapi_version='3.0',
            plugins=[MarshmallowPlugin()],
        ),
        'APISPEC_SWAGGER_URL': '/swagger/',
    })

    @app.before_request
    def before_request():
        request.request_id = _generate_request_id()

    @app.after_request
    def after_request(response):
        if not response.content_type == 'application/json':
            return response

        try:
            response_data = json.dumps(json.loads(response.data), ensure_ascii=False)
        except JSONDecodeError:
            response_data = response.data.decode('utf-8')

        logger.info(f"Response body: {response_data}")
        return response

    return app
