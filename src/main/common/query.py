import abc

from sqlalchemy import and_, or_, true

from src.main.model import Employee, Department


class QueryChain:
    def __init__(self):
        self._chains = []
        self._conditions = []

    def add(self, chain):
        self._chains.append(chain)
        return self

    def add_condition(self, condition):
        self._conditions.append(condition)
        return self

    def apply(self, query):
        query = self.concrete_apply(query)

        for condition in self._conditions:
            query = query.filter(condition.apply())

        for chain in self._chains:
            query = chain.apply(query)

        return query

    def concrete_apply(self, query):
        return query


class JoinQueryChain(QueryChain):
    def __init__(self, join_table, join_column, main_table, main_column):
        super().__init__()
        self._join_table = join_table
        self._join_column = join_column
        self._main_table = main_table
        self._main_column = main_column

    def concrete_apply(self, query):
        join_column = self._join_column
        main_column = self._main_column

        return query.join(self._join_table, join_column == main_column)


class EmployeeByNameAndLocationChain(QueryChain):
    def __init__(self, name, location):
        super().__init__()
        self._name = name
        self._location = location

    def concrete_apply(self, query):
        if self._name:
            query = query.filter(Employee.name == self._name)

        if self._location:
            query = query.filter(Department.location == self._location)

        return query


class Condition(metaclass=abc.ABCMeta):
    def apply(self):
        raise NotImplementedError("apply method must be implemented")


class EmployeeNameAndLocationCondition(Condition):
    def __init__(self, name, location, operator: str):
        self._name = name
        self._location = location
        self._operator = operator

    def apply(self):
        conditions = []

        if self._name:
            conditions.append(Employee.name == self._name)

        if self._location:
            conditions.append(Department.location == self._location)

        if self._operator == "and":
            return and_(*conditions)
        elif self._operator == "or":
            return or_(*conditions)
        else:
            raise ValueError("Invalid operator")


class LogicalOperatorCondition(Condition):
    def __init__(self, operator: str, *conditions):
        self._operator = operator
        self._conditions = conditions

    def apply(self):
        alchemy_conditions = [condition.apply() for condition in self._conditions]
        if self._operator == "and":
            return and_(*alchemy_conditions)
        elif self._operator == "or":
            return or_(*alchemy_conditions)
        else:
            raise ValueError("Invalid operator")


class EmployeeNameCondition(Condition):
    def __init__(self, name):
        self._name = name

    def apply(self):
        if self._name:
            return Employee.name == self._name

        return true()


class DepartmentLocationCondition(Condition):
    def __init__(self, location):
        self._location = location

    def apply(self):
        if self._location:
            return Department.location == self._location

        return true()
