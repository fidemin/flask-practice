import uuid

from src.main.app import db

DB_SESSION_TRANSACTION_ID = "_transaction_id"


class transaction:
    def __enter__(self):
        self._transaction_id = str(uuid.uuid4())
        if not getattr(db.session, DB_SESSION_TRANSACTION_ID, None):
            setattr(db.session, DB_SESSION_TRANSACTION_ID, self._transaction_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if getattr(db.session, DB_SESSION_TRANSACTION_ID) != self._transaction_id:
            return
        try:
            if exc_type is not None:
                db.session.rollback()
            else:
                db.session.commit()
        finally:
            delattr(db.session, DB_SESSION_TRANSACTION_ID)
