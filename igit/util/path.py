import re
from pathlib import Path, PosixPath

from igit.util.regex import FILE_SUFFIX, is_only_regex
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
        is_stem_only_regex = is_only_regex(stem)
        if is_stem_only_regex:
            # something like "*.mp4" returns True
            return bool(re.fullmatch(FILE_SUFFIX, suffix))  # nice suffix
        
        else:
            is_suffix_only_regex = is_only_regex(suffix)
            if not is_suffix_only_regex:
                return True
    return False
