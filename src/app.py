import os
import uuid
from logging.config import dictConfig

from flask import Flask, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    'filters': {
        'request_id_filter': {
            '()': "src.common.logger_setup.RequestIDFilter",
        },
    },
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s %(name)s %(request_id)s \"%(url)s\" - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout",
            "filters": ["request_id_filter"]
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"]
    },
    "loggers": {
        "src": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False
        },
        "werkzeug": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False
        }
    }
}
dictConfig(logging_config)

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


from .model import *  # noqa


def setup_config_for_db(app):
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    # app.config['SQLALCHEMY_ECHO'] = True


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_ECHO'] = True

    @app.before_request
    def before_request():
        request.request_id = _generate_request_id()

    # dictConfig(logging_config)

    setup_config_for_db(app)
    db.init_app(app)
    migrate = Migrate(app, db)

    from src.controller import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True, host="0.0.0.0", port=3000)
