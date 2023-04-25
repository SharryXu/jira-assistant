from pathlib import Path
from typing import Union


def is_absolute_path_valid(path: Union[str, Path]) -> bool:
    if path is None or not Path(path).is_absolute() or not Path(path).exists():
        return False
    return True
