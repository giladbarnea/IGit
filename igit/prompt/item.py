from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Generator, Tuple, Any, Type

from igit.util.regex import YES_OR_NO

T = TypeVar('T')


class Item(ABC, Generic[T]):
    def __init__(self, value, identifier=None) -> None:
        self.identifier = identifier
        self._val: str = value
        self._is_yes_or_no: bool = bool(YES_OR_NO.fullmatch(self._val))
    
    def __str__(self):
        # TODO: configurable
        if len(self.val) >= 80:
            return self.val[:77] + '...'
        return self.val
    
    def __repr__(self):
        string = f'[{self.identifier}], is_yes_or_no: {self.is_yes_or_no}'
        return f"""Item("{self.val}") | {string}"""
    
    @property
    def is_yes_or_no(self):
        return self._is_yes_or_no
    
    @property
    def val(self) -> str:
        return self._val
    
    @val.setter
    def val(self, val: str):
        self._val = val
        self._is_yes_or_no = bool(YES_OR_NO.fullmatch(val))


class LexicItem(Item):
    def mutate_identifier(self):
        upper = self.identifier.upper()
        self.identifier = upper
        yield upper
        words = self.val.split(' ')
        if len(words) == 1:
            raise NotImplementedError(f"no word separators, and both lowercase and uppercase identifier is taken ('{upper.lower()}')")
        words_identifiers = ''.join(map(lambda s: s[0], words))
        self.identifier = words_identifiers
        yield words_identifiers
        for i in range(len(words_identifiers)):
            new_identifiers = words_identifiers[:i] + words_identifiers[i].upper() + words_identifiers[i + 1:]
            self.identifier = new_identifiers
            yield new_identifiers
        raise StopIteration(f'mutate_identifier() exhausted all options: {repr(self)}')


class Items(Dict[str, Item], ABC):
    _itemcls = Item
    
    def __new__(cls: Type['Items'], *args: Any, **kwargs: Any) -> 'Items':
        # TODO: apply items_gen here (scratch_MyDict.py), so can init and behave like normal dict (KeywordItems())
        return super().__new__(cls, *args, **kwargs)
    
    def __init__(self, items):
        super().__init__()
        print(f'items: {items}')
        for value, identifier in self.items_gen(items):
            print(f'\tvalue: {repr(value)}', f'identifier: {repr(identifier)}', sep=' | ')
            item = self._itemcls(value, identifier)
            if item.identifier not in self:
                self.store(item)
                continue
            
            self._handle_already_exists(item)
    
    def __repr__(self):
        string = '{\n\t'
        for identifier, v in self.items():
            string += f'{repr(identifier)}: {repr(v)}\n\t'
        return string + '\n}'
    
    @abstractmethod
    def items_gen(self, items) -> Generator[Tuple[str, str], None, None]:
        ...
    
    def store(self, item: Item):
        self[item.identifier] = item
    
    def _handle_already_exists(self, item: Item):
        # overridden by LexicItems
        raise KeyError(f"item's identifier already exists in self.keys. item:\n\t{repr(item)}, self:\n\t{repr(self)}")


class KeywordItems(Items):
    def items_gen(self, kw_items: dict):
        for kw, value in kw_items.items():
            # kw is identifier
            yield value, kw


class NumItems(Items):
    def items_gen(self, num_items):
        for idx, value in enumerate(num_items):
            # idx is identifier
            yield value, str(idx)


class LexicItems(Items):
    _itemcls = LexicItem
    
    def items_gen(self, lexic_items):
        for value in lexic_items:
            # initial is identifier
            yield value, value[0]
    
    def _handle_already_exists(self, item: LexicItem):
        for mutation in item.mutate_identifier():
            if mutation in self:
                continue
            self.store(item)
