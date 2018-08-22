from lagury import tests


if __name__ == '__main__':
    tests.db_test.run()
    tests.data_node_test.run()
    tests.task_test.run()
    tests.algorithm_test.run()
