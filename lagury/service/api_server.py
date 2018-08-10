import os
import shutil
import functools
from flask import Flask, request, make_response, jsonify

from . import db, utils, loggers
from . import config as cfg


app = Flask(__name__)
logger = loggers.set_logging(os.path.join(cfg.LOGS_DIR, 'api_server.log'))


class IncorrectRequestException(Exception):
    pass


def _exception_handler(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)

        except IncorrectRequestException as ex:
            logger.exception('Got incorrect request.')
            return make_response(jsonify(dict(error='IncorrectRequestException', value=str(ex))), 400)

        except Exception as ex:
            db.session.rollback()
            logger.exception('Internal server error.')
            return make_response(jsonify(dict(error='InternalException', value=str(ex))), 500)

    return wrapped


def _check_input_arguments(data_dict, required_fields, optional_fields=None):
    if data_dict is None:
        raise IncorrectRequestException('Invalid JSON data received.')

    optional_fields = optional_fields or []

    missing_fields = [field for field in required_fields if field not in data_dict]
    redundant_fields = [field for field in data_dict if not (field in required_fields or field in optional_fields)]

    if not missing_fields and not redundant_fields:
        return

    message = ''
    if missing_fields:
        message += f'Missing JSON fields: {missing_fields}\n'
    if redundant_fields:
        message += f'Redundant JSON fields: {redundant_fields}\n'

    raise IncorrectRequestException(message)


@app.route('/task_manager/api/v1/task', methods=['POST'])
def add_task():
    """"""
    raise NotImplementedError()  # todo: implement


@app.route('/task_manager/api/v1/task/local', methods=['POST'])
@_exception_handler
def add_task_local():
    """"""
    data = request.get_json(silent=True)
    _check_input_arguments(data,
                           required_fields=['input_node_ids', 'parameters', 'launch_file_path'],
                           optional_fields=['priority'])

    input_node_ids = data['input_node_ids']
    task_parameters = data['parameters']
    launch_file_path = data['launch_file_path']
    priority = data.get('priority', 1)

    launch_file_path = os.path.abspath(launch_file_path)
    launch_dir, launch_file_name = os.path.split(launch_file_path)

    if not os.path.isfile(launch_file_path):
        raise ValueError(f'Launch file does not exist: {launch_file_path}')

    input_nodes = db.DataNode.query.filter(db.DataNode.in_(input_node_ids)).all()

    if len(input_nodes) != len(input_node_ids):
        raise ValueError('One or more input nodes do not exist.')

    output_node = db.DataNode(target_dir=utils.get_new_data_dir('output'))
    source_node = db.DataNode(target_dir=utils.get_new_data_dir('source', create_dir=False))

    shutil.copytree(launch_dir, source_node.target_dir)
    if (
            not os.path.isdir(source_node.target_dir) or
            not os.path.isfile(os.path.join(source_node.target_dir, launch_file_name))
    ):
        raise ValueError('Error copying source.')

    source_node.status = 'finished'

    task = db.Task(source_node=source_node,
                   output_node=output_node,
                   parameters=task_parameters,
                   launch_file_name=launch_file_name,
                   priority=priority)
    db.session.add(task)

    for node in input_nodes:
        task.input_nodes.append(node)

    db.session.commit()

    return jsonify(dict(task_id=int(task.id), result_node_id=int(output_node.id)))


@app.route('/task_manager/api/v1/data_node/local', methods=['POST'])
@_exception_handler
def add_data_node_local():
    """"""
    data = request.get_json(silent=True)
    _check_input_arguments(data, required_fields=['data_dir_path'], optional_fields=['description', 'copy_data'])

    data_dir_path = os.path.abspath(data['data_dir_path'])
    description = data.get('description', '')
    copy_data = data.get('copy_data', True)

    if not os.path.isdir(data_dir_path):
        raise ValueError(f'Got invalid data directory: {data_dir_path}')

    if copy_data:
        target_dir = utils.get_new_data_dir('data', create_dir=False)
        shutil.copytree(data_dir_path, target_dir)
    else:
        target_dir = data_dir_path

    data_node = db.DataNode(target_dir=target_dir, description=description, status='finished')
    db.session.add(data_node)
    db.session.commit()

    return jsonify(dict(node_id=int(data_node.id)))
