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


@api_bp.route("/departments", methods=['POST'])
def add_department():
    data = request.json
    department = Department(**data)
    db.session.add(department)
    db.session.commit()
    return jsonify(data)
