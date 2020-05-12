from pathlib import Path

import re

from util.types import PathOrStr


def dirsize(path: PathOrStr) -> int:
    """Returns size in bytes"""
    if isinstance(path, str):
        return dirsize(Path(path))
    return sum(f.lstat().st_size for f in path.glob('**/*') if f.is_file())


def has_file_suffix(path: PathOrStr) -> bool:
    """Returns True when detects file suffix, e.g. '.*/my_weird-file*v.d?.[ts]' (or 'file.txt').
    Returns False in cases like '.*/py_venv.*/' (or 'file')"""
    path = Path(path)
    suffix = path.suffix
    if suffix:
        stem = path.stem
        just_regex = re.compile(r'^[*.\\/]+$')
        is_stem_just_regex = re.match(just_regex, stem)
        if not is_stem_just_regex:
            is_suffix_just_regex = re.match(just_regex, suffix)
            if not is_suffix_just_regex:
                return True
    return False
