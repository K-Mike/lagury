import subprocess
import threading

from . import db
from . import config as cfg


def check_tasks():
    pass


def launch_task(task: db.Task):
    subprocess.run([cfg.PYTHON_INTERPRETER_PATH, task.launch_file_name], cwd=task.source_node.target_dir)


def start_service():
    pass
