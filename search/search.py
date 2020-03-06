from typing import List, Optional, Iterable

from fuzzysearch import find_near_matches

from mytool import term, util
import re


def nearest(keyword: str, collection: List[str]) -> str:
    distlist = []
    for item in collection:
        matches = find_near_matches(keyword, item, max_l_dist=len(keyword) - 1)
        distlist.append([m.dist for m in matches])
    print(term.green(f'distlist: {repr(distlist)}'))
    bestscore = 999
    bestmatch = None
    for i, dists in enumerate(distlist):
        if not dists:
            continue
        
        # [10,11] -> 10; [2,2] -> 2;
        closest = [d for d in dists if d == min(dists)]
        if not closest:
            # WEIRD, if dists, then has minimum
            from pprint import pprint as pp
            from ipdb import set_trace
            import inspect
            set_trace(inspect.currentframe(), context=50)
        
        # average-out min distances
        score = sum(closest) / len(closest)
        if score < bestscore:
            bestscore = score
            bestmatch = collection[i]
    return bestmatch


def choose_from_many(collection) -> Optional[str]:
    if collection:
        if len(collection) > 1:
            answer = util.choose(f"found {len(collection)} choices, please choose:", collection, 'continue', 'debug', 'quit')
            if answer == 'c':
                return None
            return collection[int(answer)]
        if util.ask(f'found: {collection[0]}, proceed?', 'yes', 'no (try harder)', 'debug', 'quit'):
            return collection[0]
        else:
            return None
    return None


def search(keyword: str, collection: List[str], *, criterion) -> Optional[str]:
    if criterion == 'substring':
        is_maybe = lambda k, item: k in item
    elif criterion == 'equals':
        is_maybe = lambda k, item: k == item
    else:
        raise ValueError(f'Expected criterion: "substring" | "equals", got "{criterion}"')
    
    print(term.warn(f"assuming '{criterion}' relationship between '{keyword}' and requested item..."))
    maybes = [item for item in collection if is_maybe(keyword, item)]
    choice = choose_from_many(maybes)
    if choice:
        return choice
    
    print(term.warn(f"nothing matched '{criterion}' criterion, ignoring case and word separators everywhere..."))
    regexp = re.sub(r'[-_./ ]', r'[-_./ ]?', keyword)
    maybes = [item for item in collection if re.search(regexp, item, re.IGNORECASE)]
    choice = choose_from_many(maybes)
    if choice:
        return choice
    
    print(term.warn(f"pseudo-fuzzy search failed, going full fuzzy..."))
    bestmatch = nearest(keyword, collection)
    if util.ask(f'found: {bestmatch}, proceed?', 'yes', 'no (try harder)', 'debug', 'quit'):
        return bestmatch
    else:
        return None
