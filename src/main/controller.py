import logging

from flask import request, jsonify, Blueprint

from src.main.model import Employee
from src.main.service import EmployeeService, DepartmentService
from src.main.task import copy_employee_task

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
    return jsonify(result)


@api_bp.route("/employees/<int:employee_id>/copy", methods=['POST'])
def copy_employee(employee_id):
    logger.info("Copy employee")
    # employee = EmployeeService.copy(employee_id)
    copy_employee_task.delay(employee_id)
    return jsonify({"data": "성공하였어요 🔥"})
    # return jsonify({"id": employee.employee_id})


@api_bp.route("/departments", methods=['POST'])
def add_department():
    data = request.json
    department = DepartmentService.add(data['name'], data['location'])
    return jsonify({"id": department.department_id})


@api_bp.route("/tasks", methods=['POST'])
def execute_task():
    data = request.json
    task_name = data['task_name']
    if task_name == 'copy_employee':
        task = copy_employee_task.apply_async(args=[data['data']['employee_id']])
    else:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"task_id": task.id})
