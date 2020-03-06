from typing import List

from mytool import util, term, git
import re


def _nearest_branch_alternative(branchstr, branches):
    from difflib import Differ
    d = Differ()
    bestscore = 0
    bestbranch = None
    for b in branches:
        result = list(d.compare(branchstr, b))
        score = 0
        for r in result:
            if r[0] == ' ':
                score += 1
            elif r[0] == '-':
                score -= 0.5
        if score > bestscore:
            bestbranch = b
            bestscore = score
    return bestbranch


def search(keyword: str, branches: List[str] = None) -> str:
    if not branches:
        branches = getall()
    choice = git.search(keyword, branches, criterion='substring')
    return choice


def getall() -> List[str]:
    lines = util.tryrun('git ls-remote --heads origin', printout=False).splitlines()
    return [s.partition('heads/')[2] for s in lines]


def current() -> str:
    return util.tryrun('git branch --show-current')


def version(branches: List[str] = None) -> str:
    verbranches = []
    if not branches:
        branches = getall()
    for b in branches:
        if re.fullmatch(r'recon-[\w\-_]*\d*(\.\d*){2,4}$', b):
            verbranches.append(b)
    if verbranches:
        return verbranches[-1]
    return ""
