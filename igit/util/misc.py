import functools
import inspect
import os

import re
from typing import Union, overload, Optional

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
    # content = quoted_content(string)
    # if content:
    #     return content.strip()
    # return string.strip()
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
        print('using pycharm')
    return ispycharm


def getsecret(label: str) -> str:
    import secretstorage
    con = secretstorage.dbus_init()
    col = secretstorage.get_default_collection(con)
    secret = None
    for item in col.get_all_items():
        if item.get_label() == label:
            return item.get_secret().decode()

def noop(*args,**kwargs):
    pass

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


@return_none_if_errors(ValueError, TypeError)
def safeslice(val: Union[str, int, slice]) -> slice:
    """Safe constructor for slice. Handles "2", "0:2", and ":2".
    Always returns a slice (or None if conversion fails).
    
    >>> mylist = ['first', 'second', 'third']
    >>> mylist[safeslice("1")] == mylist[safeslice(1)] == ['first']
    True
    
    >>> mylist[safeslice("0:2")] == mylist[safeslice(slice(0,2))] == ['first', 'second']
    True
    
    >>> mylist[safeslice(":2")] == mylist[safeslice(slice(2))] == ['first', 'second']
    True
    
    >>> safeslice("foo") is None
    True
    """
    
    def _to_slice(_val) -> slice:
        if isinstance(_val, slice):
            return _val
        # _stop = int(_val) + 1
        return slice(int(_val))  # may raise TypeError → None
    
    if isinstance(val, str):
        val = val.strip()
        if ':' in val:
            start, _, stop = val.partition(':')
            if start == '':  # ":2"
                start = 0
            return slice(int(start), int(stop))
    return _to_slice(val)


@return_none_if_errors(ValueError, TypeError)
def safeint(val: Union[str, int]) -> int:
    """Handles int and str ("1").
    Always returns an int (or None if cannot be used as a precise index).
    
    >>> mylist = ['first', 'second']
    >>> mylist[safeint("0")] == mylist[safeint(0)] == 'first'
    True
    
    >>> all(bad is None for bad in (safeint("0:2"), safeint(slice(0, 2)), safeint("foo")))
    True
    """
    
    if isinstance(val, str):
        val = val.strip()
    return int(val)  # may raise TypeError → None

def to_int_or_slice(val):
    """Tries converting to int, then to slice if fails.
    Finally returns None if converting to slice fails as well"""
    _int = safeint(val)
    if _int is not None:
        return _int
    _slice = safeslice(val)
    if _slice is not None:
        return _slice
    return None
def darkprint(string):
    cprint(string, 'dark')

def whiteprint(string):
    cprint(string,'white')
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
