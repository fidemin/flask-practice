from src.main.model import Employee, Department


class QueryChain:
    def __init__(self):
        self._chains = []

    def add(self, chain):
        self._chains.append(chain)
        return self

    def apply(self, query):
        query = self.concrete_apply(query)
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
