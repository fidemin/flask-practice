from unittest import TestCase

import pytest

from src.main.app import db
from src.main.model import Employee
from src.main.respository import SQLAlchemyRepository


@pytest.mark.usefixtures('setup_flask_app')
class TestSQLAlchemyRepository(TestCase):
    def test_add(self):
        repository = SQLAlchemyRepository(Employee)
        employee = Employee(name="Alice", department_id=1)

        try:
            employee = repository.add(employee)
            db.session.flush()
            actual = db.session.query(Employee).filter_by(employee_id=employee.employee_id).one()
            assert actual.name == "Alice"
            assert actual.department_id == 1
        finally:
            db.session.rollback()
