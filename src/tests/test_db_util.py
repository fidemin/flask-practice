from unittest.mock import patch

import pytest
from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine

from src.main.app import db
from src.main.common.db_util import transaction, DB_SESSION_TRANSACTION_ID


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

    db.session.rollback()
    try:
        actual = db.session.execute(temporary_table.select().filter_by(name="test")).fetchone()
    finally:
        db.session.close()
    assert actual.id == 1
    assert actual.name == "test"


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction__rollback(temporary_table):
    with pytest.raises(Exception):
        with transaction():
            db.session.execute(temporary_table.insert().values(name="test"))
            raise Exception("rollback")

    try:
        actual = db.session.execute(temporary_table.select().filter_by(name="test")).fetchone()
    finally:
        db.session.close()
    assert actual is None


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction__commit_nested_call_count_check(temporary_table):
    with patch.object(db.session, "commit") as mock_commit:
        with transaction():
            db.session.execute(temporary_table.insert().values(name="test1"))
            with transaction():
                db.session.execute(temporary_table.insert().values(name="test2"))
                with transaction():
                    db.session.execute(temporary_table.insert().values(name="test3"))

        with transaction():
            db.session.execute(temporary_table.insert().values(name="test4"))

    db.session.close()
    assert mock_commit.call_count == 2


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction__commit_nested_check_finally_commited(temporary_table):
    with transaction():
        db.session.execute(temporary_table.insert().values(name="test1"))
        with transaction():
            db.session.execute(temporary_table.insert().values(name="test2"))
            with transaction():
                db.session.execute(temporary_table.insert().values(name="test3"))

    actual_list = db.session.execute(temporary_table.select().order_by('id')).fetchall()
    assert len(actual_list) == 3
    assert getattr(db.session, DB_SESSION_TRANSACTION_ID, None) is None

    with transaction():
        db.session.execute(temporary_table.insert().values(name="test4"))

    db.session.rollback()  # to check all transaction is commited
    try:
        actual_list = db.session.execute(temporary_table.select().order_by('id')).fetchall()
    finally:
        db.session.close()
    assert len(actual_list) == 4
    assert getattr(db.session, DB_SESSION_TRANSACTION_ID, None) is None
