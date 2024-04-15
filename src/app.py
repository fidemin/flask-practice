from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))

from .models import *  # noqa


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{app.root_path}/../test.db'

    db.init_app(app)
    migrate = Migrate(app, db)

    from src.views import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True, host="0.0.0.0", port=3000)
