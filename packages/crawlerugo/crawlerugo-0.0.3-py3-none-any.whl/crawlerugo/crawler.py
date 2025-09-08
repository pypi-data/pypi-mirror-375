from collections.abc import Callable
from pathlib import Path
import os
from typing import Any

def crawl(directory: str, max_depth: int, action: Callable[[str], Any]) -> list[dict]:
    # check if directory exists / is a directory
    if not os.path.exists(directory):
        raise FileNotFoundError(f"The directory {directory} does not exist.")
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"The path {directory} is not a directory.")
    
    results = []
    root = Path(directory)

    def add_result(path_obj: Path, ret_obj: Any):
        results.append({
            'name': path_obj.name,
            'stats': path_obj if path_obj.is_file() else None,
            'callable_data': ret_obj
        })

    if max_depth < 1000:
        def _crawl(current_path: Path, current_depth: int):
            if current_depth > max_depth:
                return
            if current_path.is_dir():
                add_result(current_path, None)
                for item in current_path.iterdir():
                    _crawl(item, current_depth + 1)
            else:
                ret_obj = action(str(current_path))
                add_result(current_path, ret_obj)

        _crawl(root, 0)
    else:
        for dirpath, dirnames, filenames in os.walk(directory):
            dir_path = Path(dirpath)
            add_result(dir_path, None)
            for filename in filenames:
                file_path = dir_path / filename
                ret_obj = action(str(file_path))
                add_result(file_path, ret_obj)
    return results