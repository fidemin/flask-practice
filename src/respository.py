import abc
import logging

from .app import db

logger = logging.getLogger(__name__)


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
        logger.debug("is in transaction:" + str(db.session._proxied.in_transaction()))  # expected False
        model_obj = self._model_cls.query.get(id)
        logger.debug("is in transaction:" + str(db.session._proxied.in_transaction()))  # expected True
        return model_obj

    def delete(self, entity):
        db.session.delete(entity)
