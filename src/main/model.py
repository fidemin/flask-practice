from sqlalchemy import Enum

from src.main import db


class Employee(db.Model):
    employee_id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(Enum('M', 'F', name='gender_enum'))


class Department(db.Model):
    department_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    employees = db.relationship(
        "Employee", backref='department', primaryjoin="Department.department_id == foreign(Employee.department_id)")
