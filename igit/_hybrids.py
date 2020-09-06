from abc import abstractmethod
from typing import Dict, Optional, NoReturn, Union, overload, List

from igit_debug.investigate import loginout

from igit.cache import cachedprop
from igit.util import misc
from igit import shell, regex
from igit.search import search_and_prompt


class HybridDict(Dict[str, str]):
    """A dict / list hybrid to represent tree'ish git object, e.g. { name: SHA1 }.
    Supports getting by key (str), int (index) or slice."""
    _fetched: bool = False
    
    @classmethod
    def _fetch(cls):
        shell.runquiet('git fetch --all')
        cls._fetched = True
    
    @classmethod
    def ensurefetched(cls, fn):
        def wrap(selfarg):
            if not cls._fetched:
                cls._fetch()
            ret = fn(selfarg)
            return ret
        
        return wrap
    
    def __contains__(self, value: str):
        """Handles SHA as well as commit / tree name"""
        if regex.SHA_RE.fullmatch(value):
            # e.g. 'f5905f1' or 'f5905f1e4ab6bd82fb6644ca4cc2799a59ee725d'
            val_len = len(value)
            for bhash in map(lambda h: h[:val_len], self.hashes):
                if bhash == value:
                    return True
            return False
        return value in self
    
    @overload
    def __getitem__(self, k: slice) -> List[str]:
        """foo[1:3] → [...]"""
        ...
    
    @overload
    def __getitem__(self, k: str) -> Union[str, List[str]]:
        """If `k` is a number, returns value (str).
        If `k` is slice-like, returns a list of values.
        foo["1"] → "..."
        foo["1:3"] → [value, ...]
        """
        ...
    
    @overload
    def __getitem__(self, k: int) -> str:
        """foo[1] → '...'"""
        ...
    
    def __getitem__(self, k):
        """
        :param k: foo[1], foo["1"] → "...".
        foo[1:3], foo["1:3"] → [value, ...]
        """
        try:
            keys = list(self.keys())
            idx = misc.safeint(k)
            if idx is not None:
                return super().__getitem__(keys[idx])
            slyce = misc.safeslice(k)
            if slyce is not None:
                sliced = keys[slyce]
                return [super().__getitem__(_k) for _k in sliced]
            return super().__getitem__(k)
        except KeyError as e:
            # raised by super().__getitem__
            return self.search(k)
    
    @abstractmethod
    def current(self) -> str:
        ...
    
    @abstractmethod
    def _populate_self(self) -> NoReturn:
        ...
    
    @cachedprop
    def hashes(self):
        if not self:
            self._populate_self()
        return list(self.values())
    
    @cachedprop
    def names(self):
        if not self:
            self._populate_self()
        return list(self.keys())
    
    @loginout
    def search(self, keyword: str) -> Optional[str]:
        # TODO: option to get branch date if ambiguous etc
        if regex.SHA_RE.fullmatch(keyword):
            coll = self.hashes
        else:
            coll = self.names
        choice = search_and_prompt(keyword, coll, criterion='substring')
        return choice
