import re
from pathlib import Path, PosixPath
from typing import Union

from igit.util.regex import FILE_SUFFIX, is_only_regex
from igit.util.types import PathOrStr


class ExPath(PosixPath):
    
    def __contains__(self, other):
        return other in str(self)
    
    def subpath_of(self, other):
        return ExPath.parent_of(other, self)
    
    def parent_of(self: Union['ExPath', str], other):
        self_string = str(self)
        other_string = str(other)
        if '*' in self_string:
            if not self_string.endswith('*'):
                raise NotImplementedError("self has `*` but not in the end. self: ", self)
            self_before, wildcard, self_after = self_string.partition('*')
            if not self_before.endswith('/'):
                raise NotImplementedError("self has `*` but not preceded by '/'. self: ", self)
            if '*' in other_string:
                other_before, wildcard, other_after = other_string.partition('*')
                return ExPath.parent_of(self_before, other_before)
            return ExPath.parent_of(self_before, other)
        try:
            
            return other_string.startswith(self_string)
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
    if '.' not in path:
        return False
    suffixes = [split for split in path.split('.')[1:] if split]
    # path = Path(path)
    # suffix = path.suffix
    if not suffixes:
        return False
    stem, *_ = path.partition('.')
    # stem = path.stem
    is_stem_only_regex = is_only_regex(stem)
    if is_stem_only_regex:
        # something like "*.mp4" returns True
        return any(bool(re.fullmatch(FILE_SUFFIX, '.' + suffix)) for suffix in suffixes)  # nice suffix
    
    else:
        any_suffix_has_non_regex = any(not is_only_regex(suffix) for suffix in suffixes)
        if any_suffix_has_non_regex:
            return True
    return False
