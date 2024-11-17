import abc


class Operator(abc.ABC):
    @abc.abstractmethod
    def execute(self):
        pass
