import re
from typing import List, Dict

from igit.debug import ExcHandler
from igit.util.search import search_and_prompt

from igit.util import shell, termcolor, cachedprop


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
    
    @cachedprop
    def current(self) -> str:
        return shell.tryrun('git branch --show-current', printcmd=False, printout=False)
    
    @cachedprop
    def branches(self) -> dict:
        """{'master': <SHA1>}"""
        if not self._fetched:
            shell.tryrun('git fetch --all', printcmd=False, printout=False)
            self._fetched = True
        lines = shell.tryrun('git ls-remote --heads origin', printout=False).splitlines()
        return dict(reversed(re.match(r'(\w*)\srefs/heads/(.*)', line).groups()) for line in lines)
    
    @cachedprop
    def branchnames(self) -> List[str]:
        return list(self.branches.keys())
    
    @cachedprop
    def branchhashes(self) -> List[str]:
        return list(self.branches.values())
    
    @property
    def version(self) -> str:
        def _verstr_to_vernum(_verstr: str) -> float:
            _major = float(_verstr[:3])
            try:
                _minor = float(_verstr[3:]) / 10
            except ValueError as ve:
                _minor = 0
            _vernum = _major + _minor
            return _vernum
        
        verbranches = []
        VER_RE = re.compile(r'(\d*(\.\d*){2,4}$)')
        if verbranches:
            max_vernum: Dict[float, int] = {}
            for i, verbrch in enumerate(verbranches):
                try:
                    verstr: str = re.search(VER_RE, verbrch).groups()[0].replace('.', '')
                    vernum = _verstr_to_vernum(verstr)
                    if not max_vernum or next(iter(max_vernum)) < vernum:
                        max_vernum = {vernum: i}
                except Exception as e:
                    print('BranchTree.version()', ExcHandler(e).summary())
                    continue
            if not max_vernum:
                return verbranches[-1]
            else:
                return verbranches[next(iter(max_vernum.values()))]
    
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
