from pathlib import Path, PurePosixPath, PosixPath

import re

from igit.util.types import PathOrStr


class ExPath(PosixPath):
    
    def __contains__(self, other):
        return other in str(self)
    
    def subpath_of(self, other):
        try:
            return str(self).startswith(str(other))
        except ValueError:
            return False
    
    def parent_of(self, other):
        try:
            return str(other).startswith(str(self))
        except ValueError:
            return False


# ExPath = Path
# ExPath.__contains__ = __contains__
# ExPath.subpath_of = subpath_of
# ExPath.parent_of = parent_of


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
