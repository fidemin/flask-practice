import logging

from celery import shared_task

from src.main.service import EmployeeService

logger = logging.getLogger(__name__)


@shared_task(ignore_result=False, name="employee.employee_logger")
def employee_logger(employee_id):
    employee = EmployeeService.get_by_id(employee_id)
    logger.info(employee.name)


@shared_task(ignore_result=False, name="employee.copy_employee_task")
def copy_employee_task(employee_id):
    copied_employee = EmployeeService.copy(employee_id)
    logger.info(f"Copied employee: {employee_id} to {copied_employee.employee_id}")
