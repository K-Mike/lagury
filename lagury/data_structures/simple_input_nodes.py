import os
import numpy as np
from typing import Tuple

from ..interfaces import DataNode


class NpyInputNode(DataNode):

    def __init__(self, dir_path: str, basename: str):
        self.dir_path = dir_path
        self.basename = basename

    def get(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        X_train = np.load(os.path.join(self.dir_path, f'X_train_{self.basename}.npy'))
        y_train = np.load(os.path.join(self.dir_path, f'y_train_{self.basename}.npy'))
        X_test = np.load(os.path.join(self.dir_path, f'X_test_{self.basename}.npy'))

        return X_train, y_train, X_test

    def put(self, data):
        pass  # TODO: implement warning
