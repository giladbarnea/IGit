import os

import re
from pprint import pformat


def clip_copy(text: str):
    stripped = text.strip()
    assert '\n' not in stripped
    os.system(f'echo {stripped} | xclip -r -selection clipboard')


def unquote(string: str) -> str:
    # TODO: "gallery is MOBILE only if <= $BP3" -> "gallery is MOBILE only if <=" (maybe bcz bash?)
    string = str(string)
    try:
        
        match = re.fullmatch(r'(["\'])(.*)\1', string, re.DOTALL)
        if match:  # "'hello'"
            string = match.groups()[1]
        return string.strip()
    except Exception as e:
        import ipdb
        import inspect
        ipdb.post_mortem()
        return string


def deephash(obj):
    """Recursively calculates a hash to "unhashable" objects (and normal hashable ones)"""
    # doesnt work with: complex(...), float('nan')
    try:
        return hash(obj)
    except TypeError:
        if hasattr(obj, '__iter__'):
            if not obj:  # empty collection
                return hash(repr(obj))  # unique for () vs [] vs {} etc
            try:
                return deephash(frozenset(obj.items()))  # dict-like
            except TypeError:  # nested, non dict-like unhashable items ie { 'foo': [[5]] }
                lst = []
                for x in obj:
                    lst.append(deephash(x))
                return deephash(tuple(lst))
            except AttributeError:  # no items() method, probably a list or tuple
                lst = []
                for x in obj:
                    lst.append(deephash(x))
                return deephash(tuple(lst))
        else:
            return hash(pformat(obj))


def memoize(fn):
    """Generic memoizer to functions. Best with static functions. Example:
    ::
        @memoize
        def get_key(self, secret_name, key_name): ..."""
    memory = dict()
    if fn not in memory:
        memory[fn] = dict()
    
    def wrapper(*args, **kwargs):
        if args and kwargs:
            h = deephash(args + tuple(kwargs.items()))
        
        else:
            h = deephash(args)
        
        val = memory[fn].get(h)
        if val is None:  # put in memory
            val = fn(*args, **kwargs)
            memory[fn][h] = val
        
        return val
    
    return wrapper
