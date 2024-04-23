import abc
from contextlib import contextmanager

from .app import db


@contextmanager
def transaction():
    try:
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, id):
        raise NotImplementedError("Subclasses must implement this method")

    @abc.abstractmethod
    def add(self, entity):
        raise NotImplementedError("Subclasses must implement this method")

    @abc.abstractmethod
    def delete(self, entity):
        raise NotImplementedError("Subclasses must implement this method")


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, model_cls: db.Model):
        self._model_cls = model_cls

    def add(self, entity):
        db.session.add(entity)
        return entity

    def get_by_id(self, id):
        return self._model_cls.query.get(id)

    def delete(self, entity):
        db.session.delete(entity)
