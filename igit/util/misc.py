import functools
import inspect
import os

import re
from typing import Union, overload

from more_termcolor import cprint
import builtins


def clip_copy(text: str):
    stripped = text.strip()
    assert '\n' not in stripped
    os.system(f'echo {stripped} | xclip -r -selection clipboard')


def clean(string: str) -> str:
    return unquote(string.strip())


def unquote(string) -> str:
    # TODO: "gallery is MOBILE only if <= $BP3" -> "gallery is MOBILE only if <=" (maybe bcz bash?)
    string = str(string)
    match = re.fullmatch(r'(["\'])(.*)\1', string, re.DOTALL)
    if match:  # "'hello'"
        string = match.groups()[1]
    return string.strip()


def quote(string) -> str:
    if '"' in string:
        if "'" in string:
            raise NotImplementedError(f"quote() got string with both types of quotes, escaping not impl", string)
        return f"'{string}'"
    elif "'" in string:
        if '"' in string:
            raise NotImplementedError(f"quote() got string with both types of quotes, escaping not impl", string)
        return f'"{string}"'
    return f'"{string}"'


def trim_at(string: str, idx: int) -> str:
    if len(string) > idx:
        return f'{string[:idx - 3]}...'
    return string


def is_pycharm():
    ispycharm = 'JetBrains/Toolbox/apps/PyCharm-P' in os.environ.get('PYTHONPATH', '')
    if ispycharm:
        print('pycharm!')
    return ispycharm


def getsecret(label: str) -> str:
    import secretstorage
    con = secretstorage.dbus_init()
    col = secretstorage.get_default_collection(con)
    secret = None
    for item in col.get_all_items():
        if item.get_label() == label:
            return item.get_secret().decode()


def return_none_if_errors(*exc):
    """If no `exc` specified, returns None on any exception.
    >>> @return_none_if_errors(ValueError)
    ... def raises(exc):
    ...     raise exc()
    >>> raises(ValueError) is None
    True
    >>> raises(TypeError)
    Traceback (most recent call last):
        ...
    TypeError
    >>> @return_none_if_errors
    ... def raises(exc):
    ...     raise exc()
    >>> raises(OverflowError) is None
    True
    """
    
    def wrap(fn):
        @functools.wraps(fn)
        def decorator(*fnargs, **fnkwargs):
            
            try:
                return fn(*fnargs, **fnkwargs)
            except exc:
                return None
        
        return decorator
    
    if not exc:
        # @return_none_if_errors()    (parens but no args)
        exc = Exception
    elif inspect.isfunction(exc[0]):
        # @return_none_if_errors    (naked)
        _fn = exc[0]
        exc = Exception
        return wrap(_fn)
    
    # @return_none_if_errors(ValueError)
    return wrap


@return_none_if_errors(ValueError)
def parse_slice(val: Union[str, int, slice]) -> slice:
    """Handles int, str ("1"), str ("1:3") and slice.
    Returns None if conversion fails.
    
    string:
    
    >>> l = [0,1,2]
    >>> l[parse_slice("0")]
    [0]
    >>> l[parse_slice("0:2")]
    [0, 1]
    >>> parse_slice("foo") is None
    True
    
    int:
    
    >>> l[parse_slice(0)]
    [0]
    
    slice:
    
    >>> l[parse_slice(slice(0,2))]
    [0, 1]
    """
    
    def _to_slice(_val) -> slice:
        if isinstance(_val, slice):
            return _val
        _stop = int(_val) + 1
        return slice(_stop)
    
    if isinstance(val, str):
        val = val.strip()
        if ':' in val:
            start, _, stop = val.partition(':')
            return slice(int(start), int(stop))
    return _to_slice(val)


@return_none_if_errors(ValueError)
def parse_idx(val: Union[str, int, slice]) -> int:
    """Handles int, str ("1"), and slice.
    Returns None if conversion fails.
    
    string:

    >>> l = [0,1,2]
    >>> l[parse_idx("0")]
    0
    >>> parse_idx("0:2") is None and parse_idx("foo") is None
    True

    int:

    >>> l[parse_idx(0)]
    0

    slice:

    >>> l[parse_idx(slice(0,2))]
    0
    """
    
    def _to_idx(_val) -> int:
        if isinstance(_val, slice):
            return _val.start
        return int(_val)
    
    if isinstance(val, str):
        val = val.strip()
    return _to_idx(val)


def darkprint(string):
    cprint(string, 'dark')


def greenprint(string):
    cprint(string, 'green')


def redprint(string):
    cprint(string, 'red')


def yellowprint(string):
    cprint(string, 'yellow')


def brightyellowprint(string):
    cprint(string, 'bright yellow')


def brightredprint(string):
    cprint(string, 'bright red')


def brightwhiteprint(string):
    cprint(string, 'bright white')
