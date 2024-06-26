from logging import Formatter

from celery._state import get_current_task


class CeleryFormatter(Formatter):
    def format(self, record):
        task = get_current_task()
        if task and task.request:
            record.__dict__.update(task_id=task.request.id)
            record.__dict__.update(task_name=task.name)
        else:
            record.__dict__.setdefault('task_id', 'none')
            record.__dict__.setdefault('task_name', 'none')
        return super().format(record)
