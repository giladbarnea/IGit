import re
import string
from itertools import permutations, chain
from typing import Sized, List, Tuple, Iterable

from igit.util.regex import REGEX_CHAR


def get_permutations(s: Sized, perm_len: int, fltr=None) -> List[str]:
    """('ab', 2) → ['ab', 'ba']"""
    if perm_len > len(s):
        raise ValueError(f"arg perm_len={perm_len} greater than len(s)={len(s)}")
    if perm_len <= 0:
        raise ValueError(f"arg perm_len={perm_len} not positive")
    ret = []
    for p in permutations(s, perm_len):
        joined = ''.join(p)
        if not fltr:
            ret.append(joined)
        elif fltr(joined):
            ret.append(joined)
    return ret


def get_permutations_in_size_range(s: Sized, slc: slice, fltr=None) -> List[List[str]]:
    """('ab', slice(3)) → [['a', 'b'], ['ab', 'ba']]"""
    start = slc.start if slc.start else 1
    ret = []
    for i in range(start, slc.stop):
        perm = get_permutations(s, i, fltr)
        if perm:
            # yield perm
            ret.append(perm)
    return ret


def is_mixed_string(suffix) -> bool:
    if len(suffix) < 2:
        return False
    if re.search(r'[.\'"]+', suffix):
        return False
    has_ascii = False
    for asckii in string.ascii_letters:
        if asckii in suffix:
            has_ascii = True
            break
    if not has_ascii:
        return False
    has_punc = False
    for punc in string.punctuation:
        if punc in suffix:
            has_punc = True
            break
    if not has_punc:
        return False
    return True


def split_iter_by(coll, fn) -> Tuple[Iterable, Iterable]:
    truthies = []
    falsies = []
    for x in coll:
        if fn(x):
            truthies.append(x)
        else:
            falsies.append(x)
    return truthies, falsies


path_regexes = chain(*get_permutations_in_size_range('.*/\\', slice(5)))
mixed_suffixes = chain(*get_permutations_in_size_range(f'{REGEX_CHAR}|xml7381',
                                                       slice(6),
                                                       is_mixed_string),
                       ['xm?l', 'xm+l', 'xm.?', 'xm.+l', 'x?ml*', '[xm]*l',
                        '(x)+ml', '(x|m)l', 'x[ml]*', '(d\\.)?ts', 'x?', 'x$', '$',
                        'xml{1}', 'xml{,1}', 'xml{1,}$']
                       )

letters = string.ascii_letters + string.punctuation
