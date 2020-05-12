import re
from typing import List, Dict

from util.search import search_and_prompt

from util import shell, termcolor


class BranchTree:
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
            self._current = shell.tryrun('git branch --show-current')
        return self._current
    
    @property
    def branches(self) -> dict:
        if not self._branches:
            if not self._fetched:
                # TODO: something global
                shell.tryrun('git fetch --all', printout=False)
                self._fetched = True
            lines = shell.tryrun('git ls-remote --heads origin', printout=False).splitlines()
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
        def _verstr_to_vernum(_verstr: str) -> float:
            _major = float(_verstr[:3])
            try:
                _minor = float(_verstr[3:]) / 10
            except ValueError as e:
                _minor = 0
            _vernum = _major + _minor
            return _vernum
        
        if not self._version:
            verbranches = []
            
            for b in self.branches:
                if re.fullmatch(r'recon-[\w\-_]*\d*(\.\d*){2,4}$', b):
                    verbranches.append(b)
            if verbranches:
                max_vernum: Dict[float, int] = {}
                for i, verbrch in enumerate(verbranches):
                    try:
                        verstr: str = re.search(r'(\d*(\.\d*){2,4}$)', verbrch).groups()[0].replace('.', '')
                        vernum = _verstr_to_vernum(verstr)
                        if not max_vernum or next(iter(max_vernum)) < vernum:
                            max_vernum = {vernum: i}
                    except Exception as e:
                        continue
                if not max_vernum:
                    self._version = verbranches[-1]
                else:
                    self._version = verbranches[next(iter(max_vernum.values()))]
        return self._version
    
    def search(self, keyword: str) -> str:
        # TODO: option to get branch date if ambiguous etc
        choice = search_and_prompt(keyword, self.branchnames, criterion='substring')
        print(termcolor.green(f'choice: {choice}'))
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
