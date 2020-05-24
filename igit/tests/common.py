import re
import string
from itertools import permutations, chain
from typing import Sized, List, Tuple, Iterable

from igit.util.cache import memoize
from igit.util.regex import REGEX_CHAR

DOT_OR_QUOTE: re.Pattern = re.compile(r'[\.\'"]+')
letters_and_punc = string.ascii_letters + string.punctuation
nonregex = string.ascii_letters + string.digits + ''.join(set(string.punctuation) - set(REGEX_CHAR) - set('.'))


@memoize
def get_permutations(s: Sized, perm_len: int = None, fltr=None) -> List[str]:
    """('ab', 2) → ['ab', 'ba']"""
    s_len = len(s)
    args_repr = f'"{s if s_len < 16 else s[:7] + "..." + s[-7:]}", {perm_len}{", some filter" if fltr else ""}'
    print(f'get_permutations({args_repr})...')
    if perm_len is None:
        perm_len = min(s_len, 7)  # in 2020, r > 7 is too slow
    else:
        if perm_len > s_len:
            raise ValueError(f"arg perm_len={perm_len} greater than len(s)={s_len}")
        if perm_len <= 0:
            raise ValueError(f"arg perm_len={perm_len} not positive")
    ret = []
    for p in permutations(s, perm_len):
        joined = ''.join(p)
        if not fltr:
            ret.append(joined)
        elif fltr(joined):
            ret.append(joined)
    print(f'done get_permutations({args_repr})')
    return ret


@memoize
def iter_permutations(s: Sized, perm_len: int = None, fltr=None) -> List[str]:
    """('ab', 2) → ['ab', 'ba']"""
    s_len = len(s)
    args_repr = f'"{s if s_len < 16 else s[:7] + "..." + s[-7:]}", {perm_len}{", some filter" if fltr else ""}'
    print(f'iter_permutations({args_repr})...')
    if perm_len is None:
        perm_len = min(s_len, 7)  # in 2020, r > 7 is too slow
    else:
        if perm_len > s_len:
            raise ValueError(f"arg perm_len={perm_len} greater than len(s)={s_len}")
        if perm_len <= 0:
            raise ValueError(f"arg perm_len={perm_len} not positive")
    ret = []
    for p in permutations(s, perm_len):
        joined = ''.join(p)
        if not fltr or fltr(joined):
            yield joined
    print(f'done iter_permutations({args_repr})')
    return ret


@memoize
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


@memoize
def has_letters_and_punc(stryng) -> bool:
    if len(stryng) < 2:
        return False
    # if re.search(DOT_OR_QUOTE, stryng):
    #     return False
    has_ascii = False
    for asckii in string.ascii_letters:
        if asckii in stryng:
            has_ascii = True
            break
    if not has_ascii:
        return False
    has_punc = False
    for punc in string.punctuation:
        if punc in stryng:
            has_punc = True
            break
    if not has_punc:
        return False
    return True


@memoize
def has_regex_and_nonregex(stryng) -> bool:
    if len(stryng) < 2:
        return False
    has_nonregex = False
    for nonreg in nonregex:
        if nonreg in stryng:
            has_nonregex = True
            break
    if not has_nonregex:
        return False
    has_regex = False
    for reg in REGEX_CHAR:
        if reg in stryng:
            has_regex = True
            break
    if not has_regex:
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


# path_regexes = chain(*get_permutations_in_size_range('.*/\\', slice(5)))
@memoize
def mixed_suffixes():
    print('generating mixed_suffixes...')
    mixed_suffixes = chain(*get_permutations_in_size_range(f'{REGEX_CHAR}.xml7381',
                                                           slice(5),
                                                           has_letters_and_punc),
                           ['xm?l', 'xm+l', 'xm.?', 'xm.+l', 'x?ml*', '[xm]*l',
                            '(x)+ml', '(x|m)l', 'x[ml]*', '(d\\.)?ts', 'x?', 'x$', '$',
                            'xml{1}', 'xml{,1}', 'xml{1,}$']
                           )
    print('done generating mixed_suffixes')
    return mixed_suffixes
