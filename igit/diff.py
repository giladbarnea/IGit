from typing import List

from igit.util import cachedprop, regex
from igit.util.misc import redprint


class Diff(List[str]):
    
    def append(self, item: str, idx: int) -> None:
        if regex.SHA_RE.fullmatch(item):
            # e.g. 'f5905f1'
            if idx > 1:
                redprint(f'SHA1 items, if any, must be placed at the most in the first 2 arg slots')
                return
            if item in ctree:
                if idx == 1 and formatted[0] not in ctree:
                    redprint(f'When specifying two SHA1 args, both must belong to the same tree. 0th arg doesnt belong to ctree, 1st does')
                    return
                super().append(__object)
                return
            if item in btree:
                if i == 1 and formatted[0] not in btree:
                    redprint(f'When specifying two SHA1 args, both must belong to the same tree. 0th arg doesnt belong to btree, 1st does')
                    return
                super().append(__object)
                return
            redprint(f'item is SHA1 but not in commits nor branches. item: {repr(item)}')
            return
        
    
    @cachedprop
    def files(self):
        pass
