import pytest

from src.app import create_app


@pytest.fixture(scope='session')
def setup_flask_app():
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        yield app
