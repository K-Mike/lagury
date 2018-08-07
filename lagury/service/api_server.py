import os
import shutil
from flask import Flask, request, make_response, jsonify

from . import db, utils


app = Flask(__name__)


@app.route('/task_manager/api/v1/task', methods=['POST'])
def add_task():
    """"""
    raise NotImplementedError()  # todo: implement


@app.route('/task_manager/api/v1/task/local', methods=['POST'])
def add_task_local():
    """"""
    data = request.get_json(silent=True)

    if data is None:
        return make_response(jsonify({'error': {'value': 'Invalid JSON is given.'}}), 400)

    input_node_ids = data['input_node_ids']
    task_parameters = data['parameters']
    launch_file_path = data['launch_file_path']

    launch_file_path = os.path.abspath(launch_file_path)
    launch_dir, launch_file_name = os.path.split(launch_file_path)

    input_nodes = db.DataNode.query.filter(db.DataNode.in_(input_node_ids)).all()
    output_node = db.DataNode(target_dir=utils.get_new_data_dir('data'))
    source_node = db.DataNode(target_dir=utils.get_new_data_dir('source', create_dir=False))

    shutil.copytree(launch_dir, source_node.target_dir)
    if (
            not os.path.isdir(source_node.target_dir) or
            not os.path.isfile(os.path.join(source_node.target_dir, launch_file_name))
    ):
        raise ValueError('Error copying source.')  # todo: rollback and return JSON error

    source_node.status = 'finished'

    task = db.Task(source_node=source_node,
                   output_node=output_node,
                   parameters=task_parameters,
                   launch_file_name=launch_file_name)
    db.session.add(task)

    for node in input_nodes:
        task.input_nodes.append(node)

    db.session.commit()

    return jsonify({'task_id': int(task.id), 'result_node_id': int(output_node.id)})
