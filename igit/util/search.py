import re
from collections import defaultdict
from typing import List, Optional, Generator, Literal, Callable, Tuple, TypeVar, Dict, Generic

from fuzzysearch import find_near_matches

from igit import prompt
from igit.prompt import Special
from igit.util import termcolor
from ipdb import set_trace
import inspect

SearchCriteria = Literal['substring', 'equals', 'startswith', 'endswith']
T = TypeVar('T')


class Matches(Generic[T]):
    def __init__(self, *, maxsize):
        self.count = 0
        self.matches: Dict[float, List[T]] = defaultdict(list)
        self.worst_score = 0
        self.best_score = 999
        self._maxsize = maxsize
    
    def __bool__(self):
        return bool(self.matches)
    
    def __repr__(self):
        matches_repr = ''
        for score, candidates in self.matches.items():
            matches_repr += f'[{score}]: {", ".join(candidates)}\n    '
        return f"""Matches() ({self.count}) | best: {self.best_score} | worst: {self.worst_score}
    {matches_repr}"""
    
    def _reset_stats(self):
        # don't update best_score because we're called after discarding only worst scores
        print(termcolor.grey(f'Matches._reset_stats() beforehand: worst {self.worst_score}, count {self.count}'))
        
        self.worst_score = 0
        self.count = 0
        for score, candidates in self.matches.items():
            if score > self.worst_score:
                self.worst_score = score
            self.count += len(candidates)
    
    def append(self, item: T, score: float):
        # lower score is better
        if self.count < self._maxsize:
            # * below maxsize
            if score > self.worst_score:
                self.worst_score = score
            if score < self.best_score:
                self.best_score = score
            self.matches[score].append(item)
            self.count += 1
            return
        
        # * reached maxsize
        if score == self.worst_score:
            # even if reached max size, append item to [worst_score] because no way to decide what to discard
            self.matches[self.worst_score].append(item)
            self.count += 1
            return
        
        if score < self.worst_score:
            # better than worst; discard worst candidates, add current item
            del self.matches[self.worst_score]
            self.matches[score].append(item)
            if score < self.best_score:
                self.best_score = score
            self._reset_stats()
        
        # score is worst than worst: don't let in
    
    def best(self) -> List[T]:
        ret = self.matches[self.best_score]
        print(termcolor.grey(f'Matches.best() → {len(ret)} matches with score: {self.best_score}'))
        return ret


def nearest(keyword: str, collection: List[T], cutoff=2) -> T:
    matches = fuzzy(keyword, collection, cutoff)
    print(repr(matches))
    return matches.best()[0]


def fuzzy(keyword: str, collection: List[T], cutoff=2) -> Matches[T]:
    if not collection or not any(item for item in collection):
        raise ValueError(f"fuzzy('{keyword}', collection = {repr(collection)}): no collection")
    near_matches = Matches(maxsize=5)
    far_matches = Matches(maxsize=5)
    for item in collection:
        matches = find_near_matches(keyword, item, max_l_dist=len(keyword) - 1)
        # don't `continue` even if matches is empty
        # lower distance is better
        dists = [m.dist for m in matches]
        if not dists:
            continue
        score = sum(dists) / len(dists)
        if score >= cutoff:
            # * not so good (above cutoff): put into far_matches if within cutoff+1
            far_matches.append(item, score)
            continue
        
        # * good (below cutoff)
        near_matches.append(item, score)
    if not near_matches and not far_matches:
        print(termcolor.yellow(f'fuzzy() no near_matches nor far_matches! collection: {collection}'))
    if near_matches:
        print(termcolor.grey(f'fuzzy() → near_matches: {near_matches}\n\tfar_matches: {far_matches}'))
        return near_matches
    print(termcolor.grey(f'fuzzy() → far_matches: {far_matches}\n\tnear_matches: {near_matches}'))
    return far_matches


def _choose_from_many(collection, *promptopts) -> Optional[str]:
    if collection:
        # *  many
        if len(collection) > 1:
            i, choice = prompt.choose(f"found {len(collection)} choices, please choose:", *collection, special_opts=True)
            if choice == Special.CONTINUE:
                return None
            return collection[i]
        # *  single
        if prompt.ask(f'found: {collection[0]}. proceed with this?', no='try harder', special_opts=('debug', 'quit')):
            return collection[0]
        return None
    return None


def _create_is_maybe_predicate(criterion: SearchCriteria) -> Callable[[str, str], bool]:
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


def search_and_prompt(keyword: str, collection: List[str], criterion: SearchCriteria = 'substring') -> Optional[str]:
    """Prompts to choose from each `maybes` set and returns the choice once made"""
    for maybes, is_last in iter_maybes(keyword, collection, criterion=criterion):
        choice = _choose_from_many(maybes)
        if choice:
            return choice
    return None


def iter_maybes(keyword: str, collection: List[T], *extra_options, criterion: SearchCriteria = 'substring') -> Generator[Tuple[List[T], bool], None, None]:
    """Doesn't prompt of any kind. Yields a `[...], is_last` tuple."""
    is_maybe = _create_is_maybe_predicate(criterion)
    
    print(termcolor.yellow(f"trying to get '{keyword}' by '{criterion}'..."))
    maybes = [item for item in collection if is_maybe(item, keyword)]
    yield maybes, False
    
    print(termcolor.yellow(f"ignoring case and word separators everywhere (pseudo-fuzzy)..."))
    regexp = re.sub(r'[-_./ ]', r'[-_./ ]?', keyword)
    new_maybes = [item for item in collection if re.search(regexp, item, re.IGNORECASE)]
    if new_maybes == maybes:
        print(termcolor.yellow(f"pseudo-fuzzy got no new results"))
    else:
        yield maybes, False
    
    print(termcolor.yellow(f"going full fuzzy..."))
    near_matches = fuzzy(keyword, collection)
    print(termcolor.grey(repr(near_matches)))
    yield near_matches.best(), True
