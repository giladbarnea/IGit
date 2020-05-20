import re
from typing import Tuple, Literal, Union, NoReturn, Callable, Any, Iterable

from igit.debug.err import DeveloperError
from .util import has_duplicates
from .special import Special
from igit.util.regex import YES_OR_NO


class Options:
    opts: tuple
    kw_opts: dict
    special_opts: Tuple['Special', ...]
    
    def __init__(self, *opts: str):
        if has_duplicates(opts):
            raise ValueError(f"Duplicate opts: ", opts)
        self.opts = opts
        self.kw_opts = dict()
        self.special_opts = tuple()
        self._values = None
        self._items = None
        self._indexeditems = None
        self._all_yes_or_no = None  # calculated only when None (not True or False)
    
    def __bool__(self):
        return bool(self.opts) or bool(self.kw_opts) or bool(self.special_opts)
    
    def str(self, *, key: Literal['initial', 'index']):
        strings = []
        if key == 'initial':
            items = self.items()
        elif key == 'index':
            items = self.indexeditems()
        else:
            raise ValueError(f"key has to be either 'initial' or 'index'. key: '{key}'")
        for optkey, optval in items.items():
            strings.append(f'[{optkey}]: {optval}')
        return '\n\t'.join(strings)
    
    def __repr__(self):
        return f'Options(opts = {repr(self.opts)}, kw_opts = {repr(self.kw_opts)}, special_opts = {repr(self.special_opts)})'
    
    def set_special_options(self, special_opts: Union[str, Iterable, bool]) -> NoReturn:
        """Sets `self.special_opts` with Special objects.
        Handles passing different types of special_opts (single string, tuple of strings, or boolean), and returns a Special tuple."""
        if special_opts is True:
            self.special_opts = tuple(Special.__members__.values())
            return
        if isinstance(special_opts, str):  # 'quit'
            self.special_opts = (Special.from_full_name(special_opts),)
            return
        special_opts = tuple(map(Special.from_full_name, special_opts))
        if has_duplicates(special_opts):
            # todo: check if duplicates with normal opts? i think it's done somewhere else?
            raise ValueError(f"Duplicate special_opts: ", special_opts)
        self.special_opts = special_opts
        return None
    
    def set_kw_options(self, **kw_opts: Union[str, tuple, bool]) -> None:
        if not kw_opts:
            return
        if has_duplicates(kw_opts.values()):
            raise ValueError(f"Duplicate kw_opts: ", kw_opts)
        if 'allow_free_input' in kw_opts:
            raise DeveloperError(f"set_kw_options() 'allow_free_input' found in kw_opts, should have popped it out earlier")
        self.kw_opts = kw_opts
    
    def any_option(self, predicate: Callable[[str], Any]) -> bool:
        nonspecials = set(self.opts)
        nonspecials.update(set(self.kw_opts.values()))
        for nonspecial in nonspecials:
            if predicate(nonspecial):
                return True
        return False
    
    def all_yes_or_no(self) -> bool:
        if self._all_yes_or_no is not None:
            return self._all_yes_or_no
        nonspecials = set(self.opts)
        nonspecials.update(set(self.kw_opts.values()))
        if not nonspecials:
            self._all_yes_or_no = False
            return self._all_yes_or_no
        _all_yes_or_no = True
        for nonspecial in nonspecials:
            if not re.fullmatch(YES_OR_NO, nonspecial):
                _all_yes_or_no = False
                break
        self._all_yes_or_no = _all_yes_or_no
        return self._all_yes_or_no
    
    def values(self):
        if self._values is not None:
            return self._values
        self._values = self.items().values()
        return self._values
    
    def indexeditems(self) -> dict:
        # TODO: create an Items class (maybe also an Item class?)
        if self._indexeditems is not None:
            return self._indexeditems
        indexeditems = dict()
        for idx, opt in enumerate(self.opts):
            indexeditems[str(idx)] = opt
            
            # * self.kw_opts
        self._update_kw_opts_into_items(indexeditems)
        
        # * self.special_opts
        self._update_special_opts_into_items(indexeditems)
        
        self._indexeditems = indexeditems
        return self._indexeditems
    
    def items(self) -> dict:
        if self._items is not None:
            return self._items
        # assumes duplicates between opts, special and kw were checked already
        items = dict()
        # * self.opts
        initials = [o[0] for o in self.opts]  # initials: 'w' 'w' 's' 'i' 'a'
        for idx, opt in enumerate(self.opts):
            initial: str = opt[0]
            duplicate_idxs = [jdx for jdx, jinitial in enumerate(initials) if jinitial == initial and jdx != idx]
            if not duplicate_idxs:
                items[initial] = opt
                continue
            
            if len(duplicate_idxs) == 1:
                if initial.isupper():
                    # should handle like >= 2 duplicates
                    raise NotImplementedError("duplicate uppercase, probably one was uppercased in prev iteration: ", self.opts)
                # * opt = 'w', duplicates = ['w']
                #    transform one to 'W'
                upper = initial.upper()
                initials[idx] = upper
                items[upper] = opt
                dup_idx = duplicate_idxs[0]
                duplicate = initials[dup_idx]
                items[duplicate] = self.opts[dup_idx]
                continue
            
            if len(duplicate_idxs) == 2:
                words = opt.split(' ')
                joined = ''.join(map(lambda s: s[0], words))
                if joined in initials:
                    for j in range(len(words)):
                        new_joined = joined[:j] + joined[j].upper() + joined[j:]
                        if new_joined not in initials:
                            joined = new_joined
                            break
                    else:
                        raise NotImplementedError("duplicate multi words with no unique uppercase permutation: ", self.opts)
                
                items[joined] = opt
                dup_idx1, dup_idx2 = duplicate_idxs
                upper = initials[dup_idx1].upper()
                initials[dup_idx1] = upper
                items[upper] = self.opts[dup_idx1]
                items[initials[dup_idx2]] = self.opts[dup_idx2]
                continue
            
            raise NotImplementedError("3 duplicate options with no word separators: ", self.opts)
        
        # * self.kw_opts
        self._update_kw_opts_into_items(items)
        
        # * self.special_opts
        self._update_special_opts_into_items(items)
        
        self._items = items
        return self._items
    
    def _update_kw_opts_into_items(self, items: dict):
        for k, opt in self.kw_opts.items():
            if k in items:
                raise NotImplementedError("kw_opts clashes with items. displaying self.opts, self.kw_opts and items:",
                                          self.opts, self.kw_opts, items)
            items[k] = opt
    
    def _update_special_opts_into_items(self, items: dict):
        for spec in self.special_opts:
            if spec.value in items:
                raise NotImplementedError("special_opts clashes with items. displaying self.opts, self.kw_opts, special_opts and items:",
                                          self.opts, self.kw_opts, self.special_opts, items)
            items[spec.value] = spec.name
