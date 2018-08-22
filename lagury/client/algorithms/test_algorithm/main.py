from typing import List, Dict, Any

from lagury.client.models import Task


class SomeAlgorithm(Task):
    def __call__(self, input_dirs: List[str], output_dir: str, parameters: Dict[str, Any]):
        print('test')
