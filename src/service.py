from .model import Employee, Department
from .respository import SQLAlchemyRepository, transaction


class EmployeeService:
    def __init__(self):
        self.employee_repository = SQLAlchemyRepository(Employee)

    def get_by_id(self, employee_id):
        return self.employee_repository.get_by_id(employee_id)

    def add(self, name: str, department_id: int) -> Employee:
        with transaction():
            employee = Employee(name=name, department_id=department_id)
            employee = self.employee_repository.add(employee)
            return employee


class DepartmentService:
    def __init__(self):
        self.deployment_repository = SQLAlchemyRepository(Department)

    def add(self, name: str, location: str):
        with transaction():
            department = Department(name=name, location=location)
            return self.deployment_repository.add(department)
