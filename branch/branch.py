from typing import List, Tuple

from mytool import util, git, term
import re


class branchtree:
    """Get branch sha:
    git ls-remote --heads origin | grep dragon
    
    Get branch date:
    git log | grep -A 5 d08c5391b1fd8e249daad1ef9db4da91f70c8b9"""
    _current = ''
    _branches = dict()
    _branchnames = []
    _branchhashes = []
    _fetched = False
    _version = ''
    
    @property
    def current(self) -> str:
        if not self._current:
            self._current = util.tryrun('git branch --show-current')
        return self._current
    
    @property
    def branches(self) -> dict:
        if not self._branches:
            if not self._fetched:
                util.tryrun('git fetch --all', printout=False)
                self._fetched = True
            lines = util.tryrun('git ls-remote --heads origin', printout=False).splitlines()
            self._branches = dict(reversed(re.match(r'(\w*)\srefs/heads/(.*)', line).groups()) for line in lines)
        return self._branches
    
    @property
    def branchnames(self) -> List[str]:
        if not self._branchnames:
            self._branchnames = list(self.branches.keys())
        return self._branchnames
    
    @property
    def branchhashes(self) -> List[str]:
        if not self._branchhashes:
            self._branchhashes = list(self.branches.values())
        return self._branchhashes
    
    @property
    def version(self) -> str:
        if not self._version:
            verbranches = []
            
            for b in self.branches:
                if re.fullmatch(r'recon-[\w\-_]*\d*(\.\d*){2,4}$', b):
                    verbranches.append(b)
            if verbranches:
                self._version = verbranches[-1]
        return self._version
    
    def search(self, keyword: str) -> str:
        # TODO: option to get branch date if ambiguous etc
        for choice in git.searchalt(keyword, self.branchnames, criterion='substring'):
            print(term.green(f'choice: {choice}'))
            if not choice:
                continue
            return choice


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
    util.tryrun('git fetch --all', printout=False)
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
