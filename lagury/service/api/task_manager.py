from bottle import request

from . import api_app
from ..db import session, Task


@api_app.get('/task')
def get_all_tasks():
    tasks = Task.query.all()
    return {'data': [task.to_dict() for task in tasks]}


@api_app.post('/task')
def post_task():
    pass


@api_app.get('/task/<task_id>')
def get_task(task_id):
    task_id = int(task_id)
    return Task.query.get(task_id).to_dict()
