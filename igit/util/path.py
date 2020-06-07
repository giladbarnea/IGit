import re
from pathlib import Path, PosixPath
from typing import Union, Any, Generator

from igit.util.regex import FILE_SUFFIX, is_only_regex


class ExPath(PosixPath):
    
    def __contains__(self, other):
        return other in str(self)
    
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            if hasattr(str, name):
                ret = str(self).__getattribute__(name)
                return ret
            raise
    
    def is_dir(self) -> bool:
        """Has to exist and be a directory"""
        is_dir = super().is_dir()
        if is_dir:
            return True
        if has_file_suffix(self):
            return False
        self_string = str(self)
        if '*' in self_string:
            if not self_string.endswith('*'):
                raise NotImplementedError(f"self has `*` but not in the end. self: {self}", self)
            self_before, *_ = self_string.partition('*')
            return ExPath(self_before).is_dir()
        else:
            return False
    
    def regex(self, pattern, predicate=bool) -> Generator['ExPath', None, None]:
        """Like Path.glob(), but supports full python regex"""
        for item in filter(predicate, self.iterdir()):
            if item.is_dir():
                yield from item.regex(pattern, predicate)
                continue
            if re.match(pattern, str(item)):
                yield item
    
    def subpath_of(self, other: 'ExPathOrStr'):
        return ExPath.parent_of(other, self)
    
    def parent_of(self: 'ExPathOrStr', other):
        if not self.is_dir():
            return False
        self_string = str(self)
        other_string = str(other)
        if '*' in self_string:
            if not self_string.endswith('*'):
                raise NotImplementedError(f"self has `*` but not in the end. self: {self}", self)
            self_before, *_ = self_string.partition('*')
            if not self_before.endswith('/'):
                raise NotImplementedError(f"self has `*` but not preceded by '/'. self: {self}", self)
            if '*' in other_string:
                other_before, *_ = other_string.partition('*')
                return ExPath(self_before).parent_of(other_before)
            return ExPath(self_before).parent_of(other)
        try:
            
            return other_string.startswith(self_string)
        except ValueError:
            return False


# ExPath = Path
# ExPath.__contains__ = __contains__
# ExPath.subpath_of = subpath_of
# ExPath.parent_of = parent_of


ExPathOrStr = Union[str, ExPath]


def dirsize(path: ExPathOrStr) -> int:
    """Returns size in bytes"""
    if isinstance(path, str):
        return dirsize(Path(path))
    return sum(f.lstat().st_size for f in path.glob('**/*') if f.is_file())


def has_file_suffix(path: ExPathOrStr) -> bool:
    """Returns True when detects file suffix, e.g. '.*/my_weird-file*v.d?.[ts]' (or 'file.txt').
    Returns False in cases like '.*/py_venv.*/' (or 'file')"""
    path = str(path)
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
