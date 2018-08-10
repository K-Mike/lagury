from ..client.commands import send_local_data


def run():
    res = send_local_data(data_dir='/mnt/data/jupyter/lagury/resources/tests/test_data_node_1',
                          description='some data',
                          copy_data=False)
    print(res)
