import logging

from celery import shared_task

from src.main.operators.database import CreateLargeTableOperator
from src.main.operators.fileserver import UploadCSVFromTableOperator
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


@shared_task(ignore_result=False, name="general.upload_csv_from_table")
def upload_csv_from_table_task(**kwargs):
    table_name = kwargs.get("table_name")

    logger.info(f"Upload csv from table: {table_name}")
    operator = UploadCSVFromTableOperator(table_name=table_name)
    operator.execute()


@shared_task(ignore_result=False, name="general.create_large_table")
def create_large_table_task(**kwargs):
    logger.info(f"Create large table: {kwargs}")
    operator = CreateLargeTableOperator(**kwargs)
    operator.execute()
