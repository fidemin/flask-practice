from flask import Blueprint, request, jsonify

from .models import Department, Employee, db  # Adjust imports as necessary

api_bp = Blueprint('api', __name__)


@api_bp.route("/employees", methods=['POST'])
def add_employee():
    data = request.json
    employee = Employee(**data)
    db.session.add(employee)
    db.session.commit()
    return jsonify(data)


@api_bp.route("/employees/<int:employee_id>", methods=['GET'])
def get_employee(employee_id):
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
    department = Department(**data)
    db.session.add(department)
    db.session.commit()
    return jsonify(data)
