import logging

from flask import Blueprint, request, jsonify

from src.main.model import Employee  # Adjust imports as necessary
from src.main.service import EmployeeService, DepartmentService

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

employee_service = EmployeeService()
department_service = DepartmentService()


@api_bp.route("/employees", methods=['POST'])
def add_employee():
    data = request.json
    employee = employee_service.add(data['name'], data['department_id'])
    return jsonify({"id": employee.employee_id})


@api_bp.route("/employees/<int:employee_id>", methods=['GET'])
def get_employee(employee_id):
    logger.info(f"This is info log. get_employee: {employee_id}")
    logger.debug(f"This is debug log. get_employee: {employee_id}")
    employee_service.get_by_id(employee_id)
    employee = Employee.query.get(employee_id)
    department = employee.department
    result = {
        "name": employee.name,
        "department": department.name
    }
    return jsonify(result)


@api_bp.route("/departments", methods=['POST'])
def add_department():
    data = request.json
    department = department_service.add(data['name'], data['location'])
    return jsonify({"id": department.department_id})