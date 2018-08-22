import pprint

from ..client.commands import send_algorithm_class
from ..client.algorithms.test_algorithm import SomeAlgorithm


def run():
    r_json = send_algorithm_class(SomeAlgorithm,
                                  input_data='/mnt/data/jupyter/lagury/resources/tests/test_data_node_1',
                                  copy_data=False,
                                  parameters=dict(test_par_1='abc', test_par_2=42),
                                  description='Simple testing task')

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(r_json)
