import sys
import json
import importlib

from lagury.client.models import Task


if __name__ == '__main__':
    data = json.loads(sys.argv[1])

    input_dirs = data['input_dirs']
    output_dir = data['output_dir']
    parameters = data['parameters']

    class_path = parameters.pop('_class_path')

    if not isinstance(class_path, str):
        raise ValueError(f'Class path should be string with format: "package.module.class". Got: {class_path}')

    module_path, class_name = class_path.rsplit('.', 1)

    module = importlib.import_module(module_path)
    task_class = getattr(module, class_name)
    assert issubclass(task_class, Task)

    task_instance = task_class()
    task_instance(input_dirs, output_dir, parameters)
