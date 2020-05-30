import re
from re import Pattern

from igit.util import termcolor

BACKSLASH: str = '\\'
FILE_CHAR: str = r'[\w\d-]'
PATH_WILDCARD: str = fr'[\.\*\\]'
NOT_PATH_WILDCARD: str = r'[^\.\*\\]'
FILE_SUFFIX: Pattern = re.compile(r'\.+[\w\d]{1,4}')
# TRAILING_RE: Pattern = re.compile(fr"({PATH_WILDCARD}*{FILE_CHAR}*)({PATH_WILDCARD}*)")
# LEADING_RE: Pattern = re.compile(fr'({PATH_WILDCARD}*)(.*$)')
YES_OR_NO: Pattern = re.compile(r'(yes|no|y|n)(\s.*)?', re.IGNORECASE)
ONLY_REGEX: Pattern = re.compile(r'[\^.\\+?*()|\[\]{\}<>$]+')
ADV_REGEX_CHAR = BACKSLASH + '+()|[]{}$^<>'
ADV_REGEX_2CHAR = ['.*', '.+', '.?']
GLOB_CHAR = '?*'
REGEX_CHAR = GLOB_CHAR + ADV_REGEX_CHAR


def is_only_regex(val: str):
    if not val:
        return False
    return bool(re.fullmatch(ONLY_REGEX, val))


def endswith_regex(val: str):  # doesnt detect single dot
    if not val:
        return False
    end = val[-1]
    return end in GLOB_CHAR or end in ADV_REGEX_CHAR or val[-2:] in ADV_REGEX_2CHAR


def has_regex(val: str):  # doesnt detect single dot
    if not val:
        return False
    for i, c in enumerate(val):
        if c in GLOB_CHAR or c in ADV_REGEX_CHAR:
            return True
        try:
            if c + c[i + 1] in ADV_REGEX_2CHAR:
                return True
        except IndexError:
            pass
    return False


def has_adv_regex(val: str):  # doesnt detect single dot
    if not val:
        return False
    for i, c in enumerate(val):
        if c in ADV_REGEX_CHAR:
            return True
        try:
            if c + val[i + 1] in ADV_REGEX_2CHAR:
                return True
        except IndexError:
            pass
    return False


def make_word_separators_optional(val):
    return re.sub('[-_. ]', '[-_. ]', val)


def strip_trailing_path_wildcards(val):
    """Strips any [/.*\\] from the end. Doesn't strip from the beginning.
    Use with dirs.
    Doesn't handle file extensions well (i.e. 'py_venv.xml' loses suffix)"""
    
    match = re.match(rf"([*.\\/]*[^*.\\]*)([*.\\/]*)", val)
    groups = match.groups()
    if ''.join(groups) != val:
        print(termcolor.yellow(f"strip_trailing_path_wildcards({repr(val)}): regex stripped away too much, returning as-is. groups: {', '.join(map(repr, groups))}"))
        return val
    return groups[0]


def strip_leading_path_wildcards(val):
    """Strips any [/.*\\] from the beginning. Doesn't strip from the end.
    Use with dirs or files.
    Handles file extensions well (i.e. 'py_venv.xml' keeps suffix)"""
    match = re.match(fr'({PATH_WILDCARD}*)(.*$)', val)
    path_wildcard, rest = match.groups()
    if path_wildcard == '.':
        # not regex if dot isn't accompanied by other chars; '.git' has no regex
        return val
    return rest


def strip_surrounding_path_wildcards(val):
    """Strips any [/.*\\] from the beginning and end. Use with dirs.
    Doesn't handle file extensions well (i.e. 'py_venv.xml' loses suffix)"""
    return strip_trailing_path_wildcards(strip_leading_path_wildcards(val))
