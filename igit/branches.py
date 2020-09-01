import re
from typing import Dict

from igit_debug import ExcHandler

from igit._hybrids import HybridDict
from igit.util import cachedprop
from igit import shell


class Branches(HybridDict):
    """{ 'master' : <SHA1> }
    Get branch sha:
    git ls-remote --heads origin | grep dragon
    
    Get branch date:
    git log | grep -A 5 d08c5391b1fd8e249daad1ef9db4da91f70c8b9"""
    
    @cachedprop
    def current(self) -> str:
        return shell.runquiet('git branch --show-current')
    
    def _populate_self(self):
        return self.branches()
    
    @HybridDict.ensurefetched
    def branches(self) -> Dict[str, str]:
        lines = shell.runquiet('git ls-remote --heads origin').splitlines()
        self.clear()
        self.update(dict(reversed(re.match(r'(\w*)\srefs/heads/(.*)', line).groups()) for line in lines))
        return self
    
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
                    print('Branches.version()', ExcHandler(e).summary())
                    continue
            if not max_vernum:
                return verbranches[-1]
            else:
                return verbranches[next(iter(max_vernum.values()))]


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
