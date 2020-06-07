from typing import List


class Item:
    initial: str
    idx: int
    
    def __init__(self, opt: str, idx: int):
        self.initial = opt[0]
        self.idx = idx


class Items(dict):
    
    def __init__(self, items: List[Item]):
        super().__init__()
        items = dict()
        # initials = [o[0] for o in opts]  # initials: 'w' 'w' 's' 'i' 'a'
        for idx, opt in enumerate(items):
            initial: str = opt[0]
            duplicate_idxs = [jdx for jdx, jinitial in enumerate(initials) if jinitial == initial and jdx != idx]
            if not duplicate_idxs:
                items[initial] = opt
                continue
            
            if len(duplicate_idxs) == 1:
                if initial.isupper():
                    # should handle like >= 2 duplicates
                    raise NotImplementedError("duplicate uppercase, probably one was uppercased in prev iteration: ", opts)
                # * opt = 'w', duplicates = ['w']
                #    transform one to 'W'
                upper = initial.upper()
                initials[idx] = upper
                items[upper] = opt
                dup_idx = duplicate_idxs[0]
                duplicate = initials[dup_idx]
                items[duplicate] = opts[dup_idx]
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
                        raise NotImplementedError("duplicate multi words with no unique uppercase permutation: ", opts)
                
                items[joined] = opt
                dup_idx1, dup_idx2 = duplicate_idxs
                upper = initials[dup_idx1].upper()
                initials[dup_idx1] = upper
                items[upper] = opts[dup_idx1]
                items[initials[dup_idx2]] = opts[dup_idx2]
                continue
            
            raise NotImplementedError("3 duplicate options with no word separators: ", opts)
