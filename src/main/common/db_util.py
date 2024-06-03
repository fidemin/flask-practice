import logging
import uuid
from contextlib import ContextDecorator

from src.main.app import db

DB_SESSION_TRANSACTION_ID = "_local_transaction_id"

logger = logging.getLogger(__name__)


class Transaction(ContextDecorator):
    def __enter__(self):
        self._transaction_id = str(uuid.uuid4())
        if not getattr(db.session._proxied, DB_SESSION_TRANSACTION_ID, None):
            setattr(db.session._proxied, DB_SESSION_TRANSACTION_ID, self._transaction_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if getattr(db.session._proxied, DB_SESSION_TRANSACTION_ID) != self._transaction_id:
            return
        try:
            if exc_type is not None:
                db.session.rollback()
            else:
                db.session.commit()
        except Exception as e:
            db.session.close()
            raise e
        finally:
            delattr(db.session._proxied, DB_SESSION_TRANSACTION_ID)


def transaction(wrapped_fn=None):
    # decorator로 사용되었을 때, wrapped_fn에는 decorator로 감싼 함수가 들어온다.
    if callable(wrapped_fn):
        return Transaction()(wrapped_fn)
    # with문으로 사용되었을 때, wrapped_fn에는 None이 들어온다.
    return Transaction()
