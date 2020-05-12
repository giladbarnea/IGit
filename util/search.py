import re
from typing import List, Optional, Generator, Literal, Callable, Tuple

from fuzzysearch import find_near_matches

from ipdb import set_trace
import inspect
import difflib
import prompt
from prompt import Special
from util import termcolor

SearchCriteria = Literal['substring', 'equals', 'startswith', 'endswith']


def _nearest(collection: List[str], keyword: str) -> Generator:
    print(termcolor.green(f'_nearest() | distlist: {repr(distlist)}'))
    bestscore = 999
    bestmatch = None
    for i, dists in enumerate(distlist):
        if not dists:
            continue
        
        # [10,11] → 10; [2,2] → 2;
        closest = [d for d in dists if d == min(dists)]
        if not closest:
            # WEIRD, if dists, then has minimum
            set_trace(inspect.currentframe(), context=50)
        
        # average-out min distances # TODO: all `closest` items are the exact same number?
        score = sum(closest) / len(closest)
        if score < bestscore:
            bestscore = score
            bestmatch = collection[i]
    return bestmatch


def _near_matches(collection: List[str], keyword: str) -> List[str]:
    # distlist = []
    # avgdists = dict()
    near_matches = []
    bestscore = 999
    for item in collection:
        matches = find_near_matches(keyword, item, max_l_dist=len(keyword) - 1)
        # don't `continue` even if matches is empty
        dists = [m.dist for m in matches]
        if not dists:
            continue
        avg = sum(dists) / len(dists)
        if avg >= 2:
            continue  # arbitrary
        if avg < bestscore:
            bestscore = avg
        near_matches.append(item)
        # avgdists[item] = avg
        # distlist.append(dists)
    return near_matches


def _choose_from_many(collection, *promptopts) -> Optional[str]:
    if collection:
        # *  many
        if len(collection) > 1:
            key, choice = prompt.choose(f"found {len(collection)} choices, please choose:", *collection, special_opts=True)
            if choice == Special.CONTINUE:
                return None
            return collection[int(key)]
        # *  single
        if prompt.ask(f'found: {collection[0]}. proceed with this?', no='try harder', special_opts=('debug', 'quit')):
            return collection[0]
        else:
            return None
    return None


def _get_is_maybe_fn(criterion: SearchCriteria) -> Callable[[str, str], bool]:
    if criterion == 'substring':
        is_maybe = str.__contains__
        # is_maybe = lambda k, item: k in item
    elif criterion == 'equals':
        is_maybe = str.__eq__
        # is_maybe = lambda k, item: k == item
    elif criterion == 'startswith':
        is_maybe = str.startswith
    elif criterion == 'endswith':
        is_maybe = str.endswith
    else:
        raise ValueError(f'Expected criterion: {SearchCriteria.__args__}, got "{criterion}"')
    
    return is_maybe


def search_and_prompt(keyword: str, collection: List[str], criterion: SearchCriteria) -> Optional[str]:
    """Prompts to choose from each `maybes` set and returns the choice once made"""
    for maybes in iter_maybes(keyword, collection, criterion=criterion):
        choice = _choose_from_many(maybes)
        if choice:
            return choice
    return None


def iter_maybes(keyword: str, collection: List[str], *extra_options, criterion: SearchCriteria) -> Generator[Tuple[List[str], bool], None, None]:
    """Doesn't prompt of any kind. Yields a `[...], is_last` tuple."""
    is_maybe = _get_is_maybe_fn(criterion)
    
    print(termcolor.yellow(f"assuming '{criterion}' relationship between '{keyword}' and requested item..."))
    maybes = [item for item in collection if is_maybe(item, keyword)]
    yield maybes, False
    
    print(termcolor.yellow(f"nothing matched '{criterion}' criterion, ignoring case and word separators everywhere..."))
    regexp = re.sub(r'[-_./ ]', r'[-_./ ]?', keyword)
    maybes = [item for item in collection if re.search(regexp, item, re.IGNORECASE)]
    yield maybes, False
    
    print(termcolor.yellow(f"pseudo-fuzzy search failed, going full fuzzy..."))
    near_matches = _near_matches(collection, keyword)
    yield near_matches, True
