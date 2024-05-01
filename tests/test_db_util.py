import pytest
from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine

from src.app import db
from src.common.db_util import transaction


@pytest.fixture
def temporary_table():
    metadata = MetaData()

    table = Table(
        "test_table",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String),
    )

    engine = create_engine(db.session.get_bind().engine.url)
    metadata.create_all(engine)

    yield table

    metadata.drop_all(engine)


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction__commit(temporary_table):
    with transaction():
        db.session.execute(temporary_table.insert().values(name="test"))

    try:
        actual = db.session.execute(temporary_table.select().filter_by(name="test")).fetchone()
    finally:
        db.session.close()
    assert actual.id == 1
    assert actual.name == "test"


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction__rollback(temporary_table):
    """
    please create test for rollback transaction
    :param temporary_table:
    :return:

    """
    with pytest.raises(Exception):
        with transaction():
            db.session.execute(temporary_table.insert().values(name="test"))
            raise Exception("rollback")

    try:
        actual = db.session.execute(temporary_table.select().filter_by(name="test")).fetchone()
    finally:
        db.session.close()
    assert actual is None
