import functools
import io
import re
import string
import sys
from contextlib import contextmanager, _RedirectStream
from itertools import permutations, chain
from typing import Sized, List, Tuple, Iterable

from igit_debug import ExcHandler

from igit.util import misc
from igit.cache import memoize
from igit.regex import REGEX_CHAR

DOT_OR_QUOTE: re.Pattern = re.compile(r'[.\'"]+')
letters_and_punc = string.ascii_letters + string.punctuation

# abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\',@=:~#;-&/`_%"
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
    """Uses string.ascii_letters and string.punctutation"""
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


def forslash_always_with_dot_or_star(s):
    if '/' not in s:
        return True
    return '.' in s or '*' in s


@memoize
def path_regexes():
    print('generating path_regexes...')
    regexes = chain(*get_permutations_in_size_range('.*/\\', slice(5), forslash_always_with_dot_or_star))
    print('done getting path_regexes')
    assert all(forslash_always_with_dot_or_star(reg) for reg in regexes)  # this is necessary for some reason?
    return regexes


@memoize
def mixed_suffixes():
    print('generating mixed_suffixes...')
    suffixes = chain(*get_permutations_in_size_range(f'{REGEX_CHAR}.xml7381',
                                                     slice(5),
                                                     lambda s: has_letters_and_punc(s) and not s.endswith('.')),
                     ['xm?l', 'xm+l', 'xm.?', 'xm.+l', 'x?ml*', '[xm]*l',
                      '(x)+ml', '(x|m)l', 'x[ml]*', '(d\\.)?ts', 'x?', 'x$',
                      'xml{1}', 'xml{,1}', 'xml{1,}$']
                     )
    print('done generating mixed_suffixes')
    assert all(has_letters_and_punc(s) for s in suffixes)
    return suffixes


@contextmanager
def assert_raises(exc, *search_in_args):
    try:
        yield
    except exc as e:
        if search_in_args:
            # at least one exception arg needs to have all search strings
            if not any(all(re.search(re.escape(s), a) for s in search_in_args) for a in list(map(str, e.args))):
                raise
        pass
    except Exception as e:
        pass


def unpartial(fn):
    """
    >>> def foo(bar):
    ...     print(bar)
    >>> partial = functools.partial(foo, 'bar')
    >>> foo == unpartial(partial)
    True
    """
    origfn = fn
    while nested := getattr(origfn, 'func', None):
        origfn = nested
    return origfn


class redirect_stdin(_RedirectStream):
    _stream = 'stdin'


@contextmanager
def simulate_input(val):
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(val)
    try:
        print(f'before | sys.stdin: ', sys.stdin)
        yield
        print(f'after | sys.stdin: ', sys.stdin)
    
    finally:
        sys.stdin = old_stdin


def print_failing_cases(varname, failed_cases=None):
    """
    Prints out the value of `varname` whenever the test fails.
    Useful for functions with for loops, when you want the function to keep going even if one iteration failed.
    
    Examples:
    ::
      @print_failing_cases('n')
      def foo(*exclude):
          for n in [1,2,3]:
              if n in exclude:
                  continue
              assert n < 2
    """
    if not failed_cases:
        failed_cases = set()
    
    def decorator(testfn):
        @functools.wraps(testfn)
        def wrap():
            
            try:
                testfn()
            except AssertionError as e:
                h = ExcHandler(e)
                if varname not in h.last.locals:
                    raise ValueError(f"print_failing_cases({repr(varname)}): not in h.last.locals") from e
                val = h.last.locals.get(varname)
                failed_cases.add(val)
                
                misc.brightredprint(f'\n{unpartial(testfn).__qualname__} has failed when "{varname}" was {repr(val)}\n', 'bold')
                
                dec = print_failing_cases(varname, failed_cases)
                partial = functools.partial(testfn, *failed_cases)
                dec(partial)()
            else:
                # all failed cases are now in failed_cases, and testfn() did not raise an AssertionError.
                unpartial(testfn)()
        
        return wrap
    
    return decorator
