import os
import requests
from typing import Union, Iterable

from ..service import config as cfg


class ServerApiException(Exception):
    pass


def _check_single_input(data):
    if not isinstance(data, str) and not isinstance(data, int):
        raise ValueError(f'Single input data should be int or str. Got: {data}')
    if isinstance(data, str) and not os.path.isdir(data):
        raise ValueError(f'Input data dir does not exist: {data}')
    return data


def _create_data_nodes_if_needed(data_list, copy_data, host, port):
    data_id_list = []

    for data in data_list:
        if isinstance(data, int):
            data_id_list.append(data)
            continue

        r_json = send_local_data(data_dir=data, copy_data=copy_data, host=host, port=port)
        data_id_list.append(r_json['node_id'])

    return data_id_list


def send_local_task(launch_script_path: str,
                    input_data: Union[int, str, Iterable[Union[int, str]]],
                    copy_data=True, parameters=None, priority=1, description=None,
                    host='127.0.0.1', port=cfg.SERVER_PORT):
    """"""
    description = description or ''
    parameters = parameters or {}
    launch_script_path = os.path.abspath(launch_script_path)

    if not os.path.isfile(launch_script_path):
        raise ValueError(f'Got invalid launch script path: {launch_script_path}')

    # process input data
    if isinstance(input_data, str) or isinstance(input_data, int):
        input_data = [_check_single_input(input_data)]
    else:
        try:
            input_data = [_check_single_input(data) for data in input_data]
        except TypeError:
            raise ValueError(f'Input data should be str or int or Iterable of ints or strs. Got: {input_data}')

    input_data = _create_data_nodes_if_needed(input_data, copy_data, host, port)

    url = f'http://{host}:{port}/task_manager/api/v1/task/local'
    r = requests.post(url, json=dict(
        input_node_ids=input_data,
        parameters=parameters,
        launch_file_path=launch_script_path,
        description=description,
        copy_source=True,
        priority=priority
    ))

    if r.status_code == 200:
        return r.json()
    else:
        raise ServerApiException(f'Error: {r.status_code}\n{r.json()}')


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
        return r.json()
    else:
        raise ServerApiException(f'Error: {r.status_code}\n{r.json()}')
