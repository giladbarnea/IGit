import re
from collections import defaultdict
from typing import List, Optional, Generator, Literal, Callable, Tuple, TypeVar, Dict, Generic, Collection

from fuzzysearch import find_near_matches
from igit_debug.investigate import loginout
from igit_debug.loggr import Loggr

from igit import prompt, regex
from igit.prompt.item import Flow
from igit.util.misc import darkprint, brightyellowprint

logger = Loggr(__name__)
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
        # print(paint.faint(f'Matches._reset_stats() beforehand: worst {self.worst_score}, count {self.count}'))
        
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
        if not self.matches:
            logger.debug(f'no self.matches → returning None')
            return None
        ret = self.matches[self.best_score]
        # print(paint.faint(f'Matches.best() → {len(ret)} matches with score: {self.best_score}'))
        return ret


@loginout
def nearest(keyword: str, collection: List[T], cutoff=2) -> T:
    """Tries to get fuzzy().best()[0]. Returns None if nothing matched.
    Doesn't prompt."""
    matches = fuzzy(keyword, collection, cutoff)
    
    if matches is None:
        logger.debug(f'matches is None → returning None')
        return None
    
    # print(repr(matches))
    bestmatches = matches.best()
    if not bestmatches:
        logger.debug(f'no matches.best() → returning None')
        return None
    best = bestmatches[0]
    return best


def fuzzy(keyword: str, collection: Collection[T], cutoff=2) -> Optional[Matches[T]]:
    """Returns a `Matches` instance, or None if nothing matched.
    Doesn't prompt.
    """
    if not collection or not any(item for item in collection):
        raise ValueError(f"fuzzy('{keyword}', collection = {repr(collection)}): no collection")
    near_matches = Matches(maxsize=5)
    far_matches = Matches(maxsize=5)
    max_l_dist = min(len(keyword) - 1, 17)
    # TODO: sometimes cutoff == max_l_dist
    coll_len = len(collection)
    darkprint(f'fuzzy({repr(keyword)}, collection ({coll_len}), cutoff: {cutoff}, max_l_dist: {max_l_dist})')
    printed_progress = -1
    for i, item in enumerate(collection):
        progress = round(i / coll_len, 1)
        if progress > printed_progress:
            darkprint(f'{progress * 100}% (near_matches: {near_matches.count}, far_matches: {far_matches.count})')
            if near_matches.count ^ far_matches.count:
                # exactly one is Truthy
                coll = next(filter(bool, [near_matches, far_matches]))
                darkprint(repr(coll))
            printed_progress = progress
        matches = find_near_matches(keyword, item, max_l_dist=max_l_dist)
        # don't `continue` even if matches is empty
        # lower distance is better
        dists_sum = 0
        # dists = []
        match_lengths = 0
        match_count = 0
        for m in matches:
            dists_sum += m.dist
            # dists.append(m.dist)
            match_lengths += len(m.matched)
            match_count += 1
        if not dists_sum:
            continue
        
        # dist_score = sum(dists) / len(dists)
        dist_score = dists_sum / match_count
        avg_match_length = match_lengths / match_count
        relative_factor = avg_match_length / len(item)
        relative_factor = -round(-relative_factor - (-relative_factor % 0.2), 2)  # round up
        # relative_factor = 1 + (dist_score / len(item))
        # score = dist_score * relative_factor
        
        score = dist_score - relative_factor
        if score >= cutoff:
            # * not so good (above cutoff): put into far_matches if within cutoff+1
            far_matches.append(item, score)
            continue
        
        # * good (below cutoff)
        near_matches.append(item, score)
    if not near_matches and not far_matches:
        brightyellowprint(f'fuzzy() no near_matches nor far_matches! collection: {collection}')
        return None
    if near_matches:
        return near_matches
    darkprint(f'fuzzy() → far_matches')
    return far_matches


def _choose_from_many(collection, *promptargs, **promptkwargs) -> Optional[str]:
    if collection:
        # *  many
        if len(collection) > 1:
            i, choice = prompt.choose(f"found {len(collection)} choices, please choose:", *collection, *promptargs, flowopts=True, **promptkwargs)
            if choice == Flow.CONTINUE:
                return None
            return collection[i]
        # *  single
        if prompt.confirm(f'found: {collection[0]}. proceed with this?', no='try harder', flowopts=('debug', 'quit')):
            return collection[0]
        return None
    return None


def search_and_prompt(keyword: str, collection: Collection[str], criterion: SearchCriteria = 'substring') -> Optional[str]:
    """Prompts to choose from each of the three `maybes` sets, and returns the choice once made.
    Returns None if user "continues" until all options are exhausted"""
    for maybes, is_last in iter_maybes(keyword, collection, criterion=criterion):
        choice = _choose_from_many(maybes)
        if choice:
            return choice
    return None


def _create_is_maybe_predicate(criterion: SearchCriteria) -> Callable[[str, str], bool]:
    if criterion == 'substring':
        is_maybe = str.__contains__
    elif criterion == 'equals':
        is_maybe = str.__eq__
    elif criterion == 'startswith':
        is_maybe = str.startswith
    elif criterion == 'endswith':
        is_maybe = str.endswith
    else:
        raise ValueError(f'Expected criterion: {SearchCriteria.__args__}, got "{criterion}"')
    
    return is_maybe


def iter_maybes(keyword: str, collection: Collection[T], *extra_options, criterion: SearchCriteria = 'substring') -> Generator[Tuple[List[T], bool], None, None]:
    """Doesn't prompt. Yields three `[matches...], is_last` tuples.
    1st: str method by `criterion`
    2nd: re.search ignoring word separators
    3rd: fuzzy search (what `nearest()` uses)"""
    is_maybe = _create_is_maybe_predicate(criterion)
    
    maybes = [item for item in collection if is_maybe(item, keyword)]
    yield maybes, False
    
    regexp = None
    try:
        regexp_str = re.sub(r'[-_./ ]', r'[-_./ ]?', keyword)
        regexp = re.compile(regexp_str, re.IGNORECASE)
    except re.error:
        # compilation failed, probaby keyword is itself a regexp
        if regex.has_regex(keyword):
            regexp = re.compile(keyword, re.IGNORECASE)
    
    if regexp is not None:
        new_maybes = []
        for item in collection:
            if regexp.search(item) and item not in maybes:
                new_maybes.append(item)
        if new_maybes and new_maybes != maybes:
            yield new_maybes, False
    
    near_matches = fuzzy(keyword, collection)
    yield near_matches.best(), True
