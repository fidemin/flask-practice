import logging

from flask import request, jsonify, Blueprint

from src.main.model import Employee  # Adjust imports as necessary
from src.main.service import EmployeeService, DepartmentService
from src.main.task import employee_logger

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)


@api_bp.route("/employees", methods=['POST'])
def add_employee():
    data = request.json
    employee = EmployeeService.add(data['name'], data['department_id'])
    return jsonify({"id": employee.employee_id})


@api_bp.route("/employees", methods=['GET'])
def find_employees():
    name = request.args.get('name')
    location = request.args.get('location')
    operator = request.args.get('operator', 'and')
    gender = request.args.get('gender')
    employees = EmployeeService.find_by_name_location(name, location, operator, gender)
    return jsonify([{"name": employee.name, "location": employee.department.location} for employee in employees])


@api_bp.route("/employees/<int:employee_id>", methods=['GET'])
def get_employee(employee_id):
    logger.info(f"This is info log. get_employee: {employee_id}")
    logger.debug(f"This is debug log. get_employee: {employee_id}")
    EmployeeService.get_by_id(employee_id)
    employee = Employee.query.get(employee_id)
    department = employee.department
    result = {
        "name": employee.name,
        "department": department.name
    }
    employee_logger.delay(employee_id)
    return jsonify(result)


@api_bp.route("/departments", methods=['POST'])
def add_department():
    data = request.json
    department = DepartmentService.add(data['name'], data['location'])
    return jsonify({"id": department.department_id})
