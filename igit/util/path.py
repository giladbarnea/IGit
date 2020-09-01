import re
from pathlib import Path

from igit.expath import ExPathOrStr
from igit.regex import FILE_SUFFIX, is_only_regex


def dirsize(path: ExPathOrStr) -> int:
    """Returns size in bytes"""
    if isinstance(path, str):
        return dirsize(Path(path))
    return sum(f.lstat().st_size for f in path.glob('**/*') if f.is_file())


def has_file_suffixOLD(path: ExPathOrStr) -> bool:
    """Returns True when detects file suffix, e.g. '.*/my_weird-file*v.d?.[ts]' (or 'file.txt').
    Returns False in cases like '.*/py_venv.*/' (or 'file')
    >>> all(map(has_file_suffix, ['.*/my_weird-file*v.d?.[ts]', 'file.txt']))
    True
    >>> any(map(has_file_suffix, ['.*/py_venv.*/', 'file']))
    False
    """
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
