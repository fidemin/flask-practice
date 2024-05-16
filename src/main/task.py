import logging

from celery import shared_task

from src.main.service import EmployeeService

logger = logging.getLogger(__name__)


@shared_task(ignore_result=False)
def employee_logger(employee_id):
    employee = EmployeeService.get_by_id(employee_id)
    logger.info(employee.name)
