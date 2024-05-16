from src.main.common.db_util import transaction
from src.main.model import Employee, Department
from src.main.respository import SQLAlchemyRepository


class EmployeeService:
    _employee_repository = SQLAlchemyRepository(Employee)

    @classmethod
    def get_by_id(cls, employee_id) -> Employee:
        return cls._employee_repository.get_by_id(employee_id)

    @classmethod
    def add(cls, name: str, department_id: int) -> Employee:
        with transaction():
            employee = Employee(name=name, department_id=department_id)
            employee = cls._employee_repository.add(employee)
        return employee


class DepartmentService:
    _deployment_repository = SQLAlchemyRepository(Department)

    @classmethod
    def add(cls, name: str, location: str):
        with transaction():
            department = Department(name=name, location=location)
            return cls._deployment_repository.add(department)
