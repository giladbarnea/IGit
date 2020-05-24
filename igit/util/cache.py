import functools
from typing import Optional, Callable, Any

from igit.util.misc import deephash

UNSPECIFIED = object()


def cachedprop(_fn=None):
    def wrap(fn):
        ret = PropCache(fn)
        return ret
    
    # We're called as @cachedprop without parens.
    return wrap(_fn)


class PropCache(property):
    
    def __init__(self, fget: Optional[Callable[[Any], Any]] = None,
                 fset: Optional[Callable[[Any, Any], None]] = None,
                 fdel: Optional[Callable[[Any], None]] = None,
                 doc: Optional[str] = None) -> None:
        """fget: function TrichDay.sleep"""
        
        self._propname = fget.__name__
        super().__init__(fget, fset, fdel, doc)
    
    def __str__(self):
        return f'PropCache({self._propname})'
    
    def _try_get_from_cache(self, obj):
        """If cache doesn't exist, creates it.
        If prop doesn't exist in cache, sets it to UNSPECIFIED."""
        try:
            cached_val = obj._cache[self._propname]
            return cached_val
        
        except (AttributeError, KeyError) as e:
            # either:
            # 1) AttributeError: obj._cache wasn't defined, or
            # 2) KeyError: obj._cache was defined but did not contain prop
            # in both cases, update cache with default value
            if isinstance(e, AttributeError):
                # create cache if needed
                obj.__dict__['_cache'] = dict()
            
            obj._cache[self._propname] = UNSPECIFIED
            return UNSPECIFIED
    
    def _calculate_value(self, obj, objtype: Optional[type] = None):
        ret = super().__get__(obj, objtype)
        obj._cache[self._propname] = ret
        return ret
    
    def __get__(self, obj, objtype: Optional[type] = None):
        self._qname = f'{obj.__class__.__qualname__}.{self._propname}'
        cached_val = self._try_get_from_cache(obj)
        if cached_val is not UNSPECIFIED:
            # _calculate_value() was called before
            return cached_val
        
        # * cached_val is UNSPECIFIED
        calculated_val = self._calculate_value(obj, objtype)
        assert calculated_val is not UNSPECIFIED
        return calculated_val
    
    def __set__(self, obj, value) -> None:
        assert value is not UNSPECIFIED
        obj._cache[self._propname] = value


def memoize(fun):
    """A simple memoize decorator for functions supporting (hashable)
    positional arguments.
    It also provides a cache_clear() function for clearing the cache:

    >>> @memoize
    ... def foo()
    ...     return 1
        ...
    >>> foo()
    1
    >>> foo.cache_clear()
    >>>
    """
    
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        key = (args, frozenset(sorted(kwargs.items())))
        try:
            try:
                return cache[key]
            except TypeError as e:  # unhashable type: 'slice'
                return cache[deephash(key)]
        
        except KeyError:
            ret = fun(*args, **kwargs)
            try:
                cache[key] = ret
            except TypeError as e:  # unhashable type: 'slice'
                cache[deephash(key)] = ret
            return ret
    
    def cache_clear():
        """Clear cache."""
        cache.clear()
    
    cache = {}
    wrapper.cache_clear = cache_clear
    return wrapper
