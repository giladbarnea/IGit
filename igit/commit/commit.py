import re
from typing import List

from igit.util import shell


class CommitTree:
    _current = ''
    _commits = dict()
    _commitnames = []
    _commithashes = []
    _fetched = False
    
    @property
    def current(self) -> str:
        if not self._current:
            self._current = shell.tryrun('git rev-parse HEAD')
        return self._current
    
    @property
    def commits(self) -> dict:
        if not self._commits:
            if not self._fetched:
                shell.tryrun('git fetch --all', printout=False)
                self._fetched = True
            lines = shell.tryrun('git log --pretty=oneline', printout=False).splitlines()
            
            self._commits = dict(reversed(re.split(r' ', line, maxsplit=1)) for line in lines)
        return self._commits
    
    @property
    def commitnames(self) -> List[str]:
        if not self._commitnames:
            self._commitnames = list(self.commits.keys())
        return self._commitnames
    
    @property
    def commithashes(self) -> List[str]:
        if not self._commithashes:
            self._commithashes = list(self.commits.values())
        return self._commithashes
