from typing import List, Dict, Any


class Task:
    def __call__(self, input_dirs: List[str], output_dir: str, parameters: Dict[str, Any]):
        raise NotImplementedError()
