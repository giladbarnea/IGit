import re
from typing import List

from igit.util import shell, cachedprop


class CommitTree:
    _current = ''
    _commits = dict()
    _commitnames = []
    _commithashes = []
    _fetched = False
    
    @cachedprop
    def current(self) -> str:
        return shell.runquiet('git rev-parse HEAD')
    
    @cachedprop
    def commits(self) -> dict:
        if not self._fetched:
            shell.runquiet('git fetch --all')
            self._fetched = True
        lines = shell.runquiet('git log --pretty=oneline').splitlines()
        
        # TODO: better to just line.split(' ', maxsplit=1)?
        return dict(reversed(re.split(r' ', line, maxsplit=1)) for line in lines)
    
    @cachedprop
    def commitnames(self) -> List[str]:
        return list(self.commits.keys())
    
    @cachedprop
    def commithashes(self) -> List[str]:
        return list(self.commits.values())
