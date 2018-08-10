import os
import requests

from ..service import config as cfg


def send_local_task(launch_script_path, host='127.0.0.1', port=cfg.SERVER_PORT):
    pass


def send_local_data(data_dir, copy_data=True, description=None, host='127.0.0.1', port=cfg.SERVER_PORT):
    """"""
    description = description or ''
    data_dir = os.path.abspath(data_dir)

    if not os.path.isdir(data_dir):
        raise ValueError(f'Got invalid data directory path: {data_dir}')

    url = f'http://{host}:{port}/task_manager/api/v1/data_node/local'
    r = requests.post(url, json=dict(
        data_dir_path=data_dir,
        description=description,
        copy_data=copy_data
    ))

    if r.status_code == 200:
        print('Success')
    else:
        print(f'Error: {r.status_code}')

    return r.json()
