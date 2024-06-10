from src.main.common.db_util import transaction
from src.main.model import Employee, Department
from src.main.respository import SQLAlchemyRepository, EmployeeRepository


class EmployeeService:
    _employee_repository = EmployeeRepository()

    @classmethod
    def get_by_id(cls, employee_id) -> Employee:
        return cls._employee_repository.get_by_id(employee_id)

    @classmethod
    def find_by_name_location(cls, name: str, location: str, operator: str, gender: str) -> Employee:
        return cls._employee_repository.find_by_name_and_location(name, location, operator, gender)

    @classmethod
    @transaction
    def add(cls, name: str, department_id: int) -> Employee:
        employee = Employee(name=name, department_id=department_id)
        employee = cls._employee_repository.add(employee)
        return employee

    @classmethod
    def copy(cls, employee_id: int) -> Employee:
        with transaction():
            employee = cls._employee_repository.get_by_id(employee_id)
            new_employee = cls.add(employee.name, employee.department_id)
        return new_employee


class DepartmentService:
    _deployment_repository = SQLAlchemyRepository(Department)

    @classmethod
    @transaction
    def add(cls, name: str, location: str):
        department = Department(name=name, location=location)
        return cls._deployment_repository.add(department)
