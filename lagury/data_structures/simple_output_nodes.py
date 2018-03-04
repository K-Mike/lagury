import os
import numpy as np

from ..interfaces import DataNode


class NpyOutputNode(DataNode):

    def __init__(self, dir_path: str, basename: str):
        self.dir_path = dir_path
        self.basename = basename

    def get(self):
        pass  # TODO: implement warning

    def put(self, data: np.ndarray):
        np.save(os.path.join(self.dir_path, f'y_test_{self.basename}.npy'), data)
