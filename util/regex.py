import re
from re import Pattern

FILE_CHAR: str = r'[\w\d-]'
PATH_WILDCARD: str = r'[/\.\*\\]'
NOT_PATH_WILDCARD: str = r'[^/\.\*\\]'
FILE_SUFFIX: str = r'\.+[\w\d]*'
# TRAILING_RE: Pattern = re.compile(fr"({PATH_WILDCARD}*{FILE_CHAR}*)({PATH_WILDCARD}*)")
# LEADING_RE: Pattern = re.compile(fr'({PATH_WILDCARD}*)(.*$)')
YES_OR_NO: Pattern = re.compile(r'(yes|no|y|n)(\s.*)?', re.IGNORECASE)
REGEX_CHAR = '?+*\\.()[]{}$'


def endswith_regex(val: str):
    if not val:
        return False
    return val[-1] in REGEX_CHAR


def make_word_separators_optional(val):
    return re.sub('[-_. ]', '[-_. ]', val)


def strip_trailing_path_wildcards(val):
    """Strips any [/.*\\] from the end. Doesn't strip from the beginning.
    Use with dirs.
    Doesn't handle file extensions well (i.e. 'py_venv.xml' loses suffix)"""
    
    match = re.match(rf"([*.\\/]*[\w\d\-]*)([*.\\/]*)", val)
    groups = match.groups()
    return groups[0]


def strip_leading_path_wildcards(val):
    """Strips any [/.*\\] from the beginning. Doesn't strip from the end.
    Use with dirs or files.
    Handles file extensions well (i.e. 'py_venv.xml' keeps suffix)"""
    return re.match(fr'({PATH_WILDCARD}*)(.*$)', val).groups()[1]


def strip_surrounding_path_wildcards(val):
    """Strips any [/.*\\] from the beginning and end. Use with dirs.
    Doesn't handle file extensions well (i.e. 'py_venv.xml' loses suffix)"""
    return strip_trailing_path_wildcards(strip_leading_path_wildcards(val))
