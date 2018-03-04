class DataNode:
    """"""
    def get(self):
        raise NotImplementedError

    def put(self, data):
        raise NotImplementedError


class CoreTask:
    """"""
    def run(self, input_data: DataNode, output_data: DataNode):
        raise NotImplementedError
