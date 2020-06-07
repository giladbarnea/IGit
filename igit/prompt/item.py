from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Tuple, overload, TypeVar, Generic

from igit.util.regex import YES_OR_NO


@dataclass
class Item:
    val: str
    initial: str
    idx: str
    kw: str = field(default=None, init=False)
    is_yes_or_no: bool = field(default=False, init=False)
    
    def __init__(self, idx: str, item, kw: str = None) -> None:
        self.val = item
        self.idx = idx
        self.initial = item[0]
        self.kw = kw
    
    def __str__(self):
        return self.val
    
    def __post_init__(self):
        self.is_yes_or_no = bool(YES_OR_NO.fullmatch(self.val))
    
    def mutate_initial(self):
        upper = self.initial.upper()
        self.initial = upper
        yield upper
        words = self.val.split(' ')
        if len(words) == 1:
            raise NotImplementedError(f"no word separators, and both lowercase and uppercase initial is taken ('{upper.lower()}')")
        words_initials = ''.join(map(lambda s: s[0], words))
        self.initial = words_initials
        yield words_initials
        for i in range(len(words_initials)):
            new_initials = words_initials[:i] + words_initials[i].upper() + words_initials[i + 1:]
            self.initial = new_initials
            yield new_initials
        raise StopIteration(f'mutate_initial() exhausted all options: {repr(self)}')


class Items(dict):
    @overload
    def __init__(self, items: dict):
        ...
    
    @overload
    def __init__(self, items: Tuple[str]):
        ...
    
    def __init__(self, items):
        super().__init__()
        
        for idx, *args in self.items_gen(items):
            item = Item(str(idx), *args)
            if item.initial not in self:
                self.store(item)
                continue
            
            for mutation in item.mutate_initial():
                if mutation not in self:
                    self.store(item)
                    continue
    
    def items_gen(self, items):
        for idx, *args in enumerate(items):
            yield idx, *args
    
    @abstractmethod
    def store(self, item: Item):
        ...
    
    def by_initial(self):
        return
    
    def by_index(self):
        return


class KeywordItems(Items, dict):
    
    def items_gen(self, kw_items: dict):
        for idx, (kw, itm) in enumerate(kw_items.items()):
            yield idx, itm, kw
    
    def store(self, item: Item):
        self[item.kw] = item


class IndexedItems(Items):
    def store(self, item: Item):
        self[item.idx] = item


class LexicItems(Items):
    def store(self, item: Item):
        self[item.initial] = item
