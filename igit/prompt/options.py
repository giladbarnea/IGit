from abc import ABC
from contextlib import suppress
from typing import Tuple, Union, NoReturn, Callable, Any, Iterable

from igit.debug import ExcHandler
from igit.debug.err import DeveloperError
from igit.prompt.item import Items, NumItems, LexicItems, KeywordItems, Item
from igit.prompt.special import Special
from igit.prompt.util import has_duplicates
from igit.util.cache import memoize
from more_termcolor import colors, colored
from ipdb import set_trace
import inspect


class Options(ABC):
    # items: Items
    _itemscls = None
    
    # special_opts: Tuple['Special', ...]
    
    def __init__(self, *opts: str):
        self.items = self._itemscls(opts)
        if has_duplicates(opts):
            raise ValueError(f"Duplicate opts: ", opts)
        # self.special_opts = tuple()
        # self._values = None
        # self._items = None
        # self._indexeditems = None
        # self._all_yes_or_no = None  # calculated only when None (not True or False)
    
    def __bool__(self):
        # return bool(self.items) or bool(self.special_opts)
        return bool(self.items)
    
    def __repr__(self):
        # return f'Options(opts = {repr(self.items)}, special_opts = {repr(self.special_opts)})'
        return f'Options(opts = {repr(self.items)})'
    
    def set_special_options(self, special_opts: Union[str, Iterable, bool]) -> NoReturn:
        """Sets `self.special_opts` with Special objects.
        Handles passing different types of special_opts (single string, tuple of strings, or boolean), and returns a Special tuple."""
        if special_opts is True:
            special_opts = tuple(Special.__members__.values())
        elif isinstance(special_opts, str):  # 'quit'
            special_opts = (Special.from_full_name(special_opts),)
        else:
            special_opts = tuple(map(Special.from_full_name, special_opts))
            if has_duplicates(special_opts):
                # todo: check if duplicates with normal opts? i think it's done somewhere else?
                raise ValueError(f"Duplicate special_opts: ", special_opts)
        
        for special in special_opts:
            self.items.update({special.value: special.name})
        return None
    
    def set_kw_options(self, **kw_opts: Union[str, tuple, bool]) -> None:
        if not kw_opts:
            return
        if has_duplicates(kw_opts.values()):
            raise ValueError(f"Duplicate kw_opts: ", kw_opts)
        if 'free_input' in kw_opts:
            raise DeveloperError(f"set_kw_options(): 'free_input' found in kw_opts, should have popped it out earlier")
        non_special_kw_opts = dict()
        for kw in kw_opts:
            opt = kw_opts[kw]
            if kw in self.items:
                raise ValueError(f"set_kw_options(): '{kw}' in kw_opts but was already in self.items", repr(self))
            try:
                special = Special.from_full_name(opt)
            except ValueError:
                non_special_kw_opts[kw] = opt
            else:
                self.items[kw] = special.name
        
        if not non_special_kw_opts:
            return
        
        kw_items = KeywordItems(non_special_kw_opts)
        
        self.items.update(**kw_items)
        # self.kw_opts = kw_opts
    
    def any_item(self, predicate: Callable[[Item], Any]) -> bool:
        for item in self.items.values():
            if predicate(item):
                return True
        return False
    
    def all_yes_or_no(self) -> bool:
        
        for item in self.items.values():
            try:
                if not item.is_yes_or_no:
                    return False
            except AttributeError:
                print(colors.brightblack(f'Options.all_yes_or_no() AttributeError with item: {item} {type(item)}. Ignoring.'))
        return True
        
        # nonspecials = set(self.opts)
        # nonspecials.update(set(self.kw_opts.values()))
        # if not nonspecials:
        #     return False
        # all_yes_or_no = True
        # for nonspecial in nonspecials:
        #     if not re.fullmatch(YES_OR_NO, nonspecial):
        #         all_yes_or_no = False
        #         break
        # return all_yes_or_no
    
    # @cachedprop
    # def indexeditems(self) -> dict:
    #     # TODO: create an Items class (maybe also an Item class?)
    #     indexeditems = dict()
    #     for idx, opt in enumerate(self.opts):
    #         indexeditems[str(idx)] = opt
    #
    #         # * self.kw_opts
    #     self._update_kw_opts_into_items(indexeditems)
    #
    #     # * self.special_opts
    #     self._update_special_opts_into_items(indexeditems)
    #
    #     return indexeditems
    
    # @cachedprop
    # def items(self) -> dict:
    #     # assumes duplicates between opts, special and kw were checked already
    #     items = dict()
    #     # * self.opts
    #     initials = [o[0] for o in self.opts]  # initials: 'w' 'w' 's' 'i' 'a'
    #     for idx, opt in enumerate(self.opts):
    #         initial: str = opt[0]
    #         duplicate_idxs = [jdx for jdx, jinitial in enumerate(initials) if jinitial == initial and jdx != idx]
    #         if not duplicate_idxs:
    #             items[initial] = opt
    #             continue
    #
    #         if len(duplicate_idxs) == 1:
    #             if initial.isupper():
    #                 # should handle like >= 2 duplicates
    #                 raise NotImplementedError("duplicate uppercase, probably one was uppercased in prev iteration: ", self.opts)
    #             # * opt = 'w', duplicates = ['w']
    #             #    transform one to 'W'
    #             upper = initial.upper()
    #             initials[idx] = upper
    #             items[upper] = opt
    #             dup_idx = duplicate_idxs[0]
    #             duplicate = initials[dup_idx]
    #             items[duplicate] = self.opts[dup_idx]
    #             continue
    #
    #         if len(duplicate_idxs) == 2:
    #             words = opt.split(' ')
    #             joined = ''.join(map(lambda s: s[0], words))
    #             if joined in initials:
    #                 for j in range(len(words)):
    #                     new_joined = joined[:j] + joined[j].upper() + joined[j:]
    #                     if new_joined not in initials:
    #                         joined = new_joined
    #                         break
    #                 else:
    #                     raise NotImplementedError("duplicate multi words with no unique uppercase permutation: ", self.opts)
    #
    #             items[joined] = opt
    #             dup_idx1, dup_idx2 = duplicate_idxs
    #             upper = initials[dup_idx1].upper()
    #             initials[dup_idx1] = upper
    #             items[upper] = self.opts[dup_idx1]
    #             items[initials[dup_idx2]] = self.opts[dup_idx2]
    #             continue
    #
    #         raise NotImplementedError("3 duplicate options with no word separators: ", self.opts)
    #
    #     # * self.kw_opts
    #     self._update_kw_opts_into_items(items)
    #
    #     # * self.special_opts
    #     self._update_special_opts_into_items(items)
    #
    #     return items
    
    # def _update_kw_opts_into_items(self, items: dict):
    #     for k, opt in self.kw_opts.items():
    #         if k in items:
    #             raise NotImplementedError("kw_opts clashes with items. displaying self.opts, self.kw_opts and items:",
    #                                       self.opts, self.kw_opts, items)
    #         items[k] = opt
    #
    # def _update_special_opts_into_items(self, items: dict):
    #     for spec in self.special_opts:
    #         if spec.value in items:
    #             raise NotImplementedError("special_opts clashes with items. displaying self.opts, self.kw_opts, special_opts and items:",
    #                                       self.opts, self.kw_opts, self.special_opts, items)
    #         items[spec.value] = spec.name


class NumOptions(Options):
    _itemscls = NumItems
    items: NumItems
    
    def __init__(self, *opts: str):
        self.items = NumItems(opts)
        super().__init__(*opts)


class LexicOptions(Options):
    items: LexicItems
    
    def __init__(self, *opts: str):
        self.items = LexicItems(opts)
        super().__init__(*opts)
