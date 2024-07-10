from unittest.mock import patch

import pytest
from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine

from src.main import db
from src.main.common.db_util import DB_SESSION_TRANSACTION_ID, transaction


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
    try:
        metadata.create_all(engine)
        yield table
    finally:
        metadata.drop_all(engine)


@pytest.fixture
def session_close():
    yield
    db.session.close()


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction__commit(temporary_table, session_close):
    with transaction():
        db.session.execute(temporary_table.insert().values(name="test"))

    db.session.rollback()  # to check all transaction is commited

    actual = db.session.execute(temporary_table.select().filter_by(name="test")).fetchone()
    assert actual.id == 1
    assert actual.name == "test"


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction__rollback(temporary_table, session_close):
    with pytest.raises(Exception):
        with transaction():
            db.session.execute(temporary_table.insert().values(name="test"))
            raise Exception("rollback")

    actual = db.session.execute(temporary_table.select().filter_by(name="test")).fetchone()
    assert actual is None


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction__commit_nested_call_count_check(temporary_table, session_close):
    with patch.object(db.session, "commit") as mock_commit:
        with transaction():
            db.session.execute(temporary_table.insert().values(name="test1"))
            with transaction():
                db.session.execute(temporary_table.insert().values(name="test2"))
                with transaction():
                    db.session.execute(temporary_table.insert().values(name="test3"))

        with transaction():
            db.session.execute(temporary_table.insert().values(name="test4"))

    assert mock_commit.call_count == 2


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction__rollback_nested_call_count_check(temporary_table, session_close):
    with pytest.raises(ValueError):
        with patch.object(db.session, "rollback") as mock_rollback:
            with transaction():
                db.session.execute(temporary_table.insert().values(name="test1"))
                with transaction():
                    db.session.execute(temporary_table.insert().values(name="test2"))
                    with transaction():
                        db.session.execute(temporary_table.insert().values(name="test3"))
                        raise ValueError("rollback")

    assert mock_rollback.call_count == 1


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction__rollback_nested_finally_rollback(temporary_table, session_close):
    with pytest.raises(ValueError):
        with transaction():
            db.session.execute(temporary_table.insert().values(name="test1"))
            with transaction():
                db.session.execute(temporary_table.insert().values(name="test2"))
                with transaction():
                    db.session.execute(temporary_table.insert().values(name="test3"))

                # 일부러 중간에 rollback을 호출하여 전체 rollback이 되는지 확인
                raise ValueError("rollback")

    actual_list = db.session.execute(temporary_table.select().order_by('id')).fetchall()
    assert len(actual_list) == 0
    assert getattr(db.session._proxied, DB_SESSION_TRANSACTION_ID, None) is None


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction__commit_nested_check_finally_commited(temporary_table, session_close):
    with transaction() as first_transaction:
        db.session.execute(temporary_table.insert().values(name="test1"))
        with transaction():
            db.session.execute(temporary_table.insert().values(name="test2"))
            with transaction():
                db.session.execute(temporary_table.insert().values(name="test3"))
                assert getattr(db.session._proxied, DB_SESSION_TRANSACTION_ID, None) is not None
                assert first_transaction._transaction_id == db.session._proxied._local_transaction_id

    actual_list = db.session.execute(temporary_table.select().order_by('id')).fetchall()
    assert len(actual_list) == 3
    assert getattr(db.session._proxied, DB_SESSION_TRANSACTION_ID, None) is None

    with transaction():
        db.session.execute(temporary_table.insert().values(name="test4"))

    db.session.rollback()  # to check all transaction is commited
    actual_list = db.session.execute(temporary_table.select().order_by('id')).fetchall()
    assert len(actual_list) == 4
    assert getattr(db.session._proxied, DB_SESSION_TRANSACTION_ID, None) is None


@transaction
def commit_func(table: Table):
    db.session.execute(table.insert().values(name="test"))


@transaction
def commit_func1(table: Table):
    db.session.execute(table.insert().values(name="test1"))
    commit_func2(table)


@transaction
def commit_func2(table: Table):
    db.session.execute(table.insert().values(name="test2"))
    commit_func3(table)


@transaction
def commit_func3(table: Table):
    db.session.execute(table.insert().values(name="test3"))


@transaction
def rollback_func1(table: Table):
    db.session.execute(table.insert().values(name="test"))
    raise ValueError("rollback")


@transaction
def rollback_func2(table: Table):
    db.session.execute(table.insert().values(name="test"))
    commit_func3(table)
    raise ValueError("rollback")


@transaction
def nested_rollback_func(table: Table):
    db.session.execute(table.insert().values(name="test1"))
    rollback_func2(table)


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction_decorator__commit(temporary_table, session_close):
    commit_func(temporary_table)

    db.session.rollback()  # to check all transaction is commited
    actual = db.session.execute(temporary_table.select().filter_by(name="test")).fetchone()
    assert actual.id == 1
    assert actual.name == "test"


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction_decorator__rollback(temporary_table, session_close):
    with pytest.raises(ValueError):
        rollback_func1(temporary_table)

    actual = db.session.execute(temporary_table.select().filter_by(name="test")).fetchone()
    assert actual is None


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction_decorator__commit_nested_call_count_check(temporary_table, session_close):
    with patch.object(db.session, "commit") as mock_commit:
        commit_func1(temporary_table)
        commit_func(temporary_table)
    assert mock_commit.call_count == 2


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction_decorator__rollback_nested_call_count_check(temporary_table, session_close):
    with pytest.raises(ValueError):
        with patch.object(db.session, "rollback") as mock_rollback:
            nested_rollback_func(temporary_table)
    assert mock_rollback.call_count == 1


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction_decorator__rollback_nested_finally_rollback(temporary_table, session_close):
    with pytest.raises(ValueError):
        nested_rollback_func(temporary_table)

    actual_list = db.session.execute(temporary_table.select().order_by('id')).fetchall()
    assert len(actual_list) == 0
    assert getattr(db.session._proxied, DB_SESSION_TRANSACTION_ID, None) is None


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction_decorator__commit_nested_check_finally_commited(temporary_table, session_close):
    commit_func1(temporary_table)

    actual_list = db.session.execute(temporary_table.select().order_by('id')).fetchall()
    assert len(actual_list) == 3
    assert getattr(db.session._proxied, DB_SESSION_TRANSACTION_ID, None) is None

    commit_func(temporary_table)

    db.session.rollback()  # to check all transaction is commited

    actual_list = db.session.execute(temporary_table.select().order_by('id')).fetchall()
    assert len(actual_list) == 4
    assert getattr(db.session._proxied, DB_SESSION_TRANSACTION_ID, None) is None


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction_context_decorator_mixed__commit_nested_call_count_check(temporary_table, session_close):
    with patch.object(db.session, "commit") as mock_commit:
        with transaction() as first_transaction:
            db.session.execute(temporary_table.insert().values(name="test"))
            commit_func1(temporary_table)

        commit_func1(temporary_table)

    assert mock_commit.call_count == 2


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction_context_decorator_mixed__rollback_nested_call_count_check(temporary_table, session_close):
    with pytest.raises(ValueError):
        with patch.object(db.session, "rollback") as mock_rollback:
            with transaction():
                db.session.execute(temporary_table.insert().values(name="test"))
                rollback_func2(temporary_table)

    assert mock_rollback.call_count == 1


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction_context_decorator_mixed_finally_commited(temporary_table, session_close):
    with transaction() as first_transaction:
        db.session.execute(temporary_table.insert().values(name="test"))
        commit_func1(temporary_table)
        assert getattr(db.session._proxied, DB_SESSION_TRANSACTION_ID, None) == first_transaction._transaction_id

    actual_list = db.session.execute(temporary_table.select().order_by('id')).fetchall()
    assert len(actual_list) == 4
    assert getattr(db.session._proxied, DB_SESSION_TRANSACTION_ID, None) is None

    commit_func(temporary_table)

    db.session.rollback()  # to check all transaction is commited

    actual_list = db.session.execute(temporary_table.select().order_by('id')).fetchall()
    assert len(actual_list) == 5
    assert getattr(db.session._proxied, DB_SESSION_TRANSACTION_ID, None) is None


@pytest.mark.usefixtures("setup_flask_app")
def test_transaction_context_decorator_mixed__rollback_nested_finally_rollback(temporary_table, session_close):
    with pytest.raises(ValueError):
        with transaction():
            db.session.execute(temporary_table.insert().values(name="test"))
            rollback_func2(temporary_table)

    actual_list = db.session.execute(temporary_table.select().order_by('id')).fetchall()
    assert len(actual_list) == 0
    assert getattr(db.session._proxied, DB_SESSION_TRANSACTION_ID, None) is None
