import pprint

from ..client.commands import send_local_task
from .template_tasks_tests import xlsx_to_csv_task


def run():
    launch_script_path = xlsx_to_csv_task.main.__file__
    print(launch_script_path)

    r_json = send_local_task(launch_script_path,
                             input_data='/mnt/data/jupyter/lagury/resources/tests/test_data_node_1',
                             copy_data=False,
                             parameters=dict(test_par_1='abc', test_par_2=42),
                             description='Simple testing task')

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(r_json)
