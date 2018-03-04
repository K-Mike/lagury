from sklearn.svm import LinearSVC

from ..interfaces import CoreTask
from ..data_structures import NpyInputNode, NpyOutputNode


class LinearSvcTask(CoreTask):

    def __init__(self, **model_params):
        self.model_params = model_params
        self.model = LinearSVC(**model_params)

    def run(self, input_data: NpyInputNode, output_data: NpyOutputNode):
        X_train, y_train, X_test = input_data.get()

        self.model.fit(X_train, y_train)
        y_test = self.model.predict(X_test)

        output_data.put(y_test)
