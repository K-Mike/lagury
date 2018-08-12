import os
import subprocess
import threading
import logging
import json
import time

from . import db
from . import config as cfg
from .loggers import set_logging, StreamToLogger
from .api_server import app


def launch_task(task: db.Task):
    """"""
    logger_path = os.path.join(task.output_node.target_dir, 'log.txt')
    logger = set_logging(logger_path)

    meta = dict(
        input_dirs=[node.target_dir for node in task.input_nodes],
        output_dir=task.output_node.target_dir,
        parameters=task.parameters
    )

    task.status = 'running'
    db.session.commit()

    try:
        subprocess.run(
            [cfg.PYTHON_INTERPRETER_PATH, task.launch_file_name, json.dumps(meta)],
            cwd=task.source_node.target_dir,
            stdout=StreamToLogger(logger, logging.INFO),
            stderr=StreamToLogger(logger, logging.ERROR),
            check=True
        )

        task.status = 'finished'
        task.output_node.status = 'finished'
        db.session.commit()

    except subprocess.CalledProcessError:
        task.status = 'failed'
        task.output_node.status = 'failed'
        db.session.commit()


def worker(worker_id: int):
    """"""
    logger = set_logging(os.path.join(cfg.LOGS_DIR, 'core.log'))

    while True:
        time.sleep(10)
        try:
            task = db.Task.get_pending()

            if task is None:
                continue

            logger.info(f'Launching task {task.id} with parameters {task.parameters} in worker {worker_id}')
            launch_task(task)
            logger.info(f'Task {task.id} completed in worker {worker_id}. '
                        f'Results saved to:\n{task.output_node.target_dir}')

        except Exception:
            logger.exception(f'Exception occurred in worker {worker_id}')


def start_service():
    """"""
    # starting workers
    worker_thread = threading.Thread(target=worker, args=(0,))
    worker_thread.start()

    # todo: running server locally in debug mode for now
    app.run(port=cfg.SERVER_PORT, debug=True)
