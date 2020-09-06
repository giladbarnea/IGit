import re
from typing import Dict

from igit._hybrids import HybridDict
from igit.cache import cachedprop
from igit import shell


class Commits(HybridDict):
    """{ commit_message: <SHA1> }"""
    
    @cachedprop
    def current(self) -> str:
        return shell.runquiet('git rev-parse HEAD')
    
    def _populate_self(self):
        return self.commits()
    
    @HybridDict.ensurefetched
    def commits(self) -> Dict[str, str]:
        lines = shell.runquiet('git log --pretty=oneline').splitlines()
        self.clear()
        # TODO: better to just line.split(' ', maxsplit=1)?
        self.update(dict(reversed(re.split(r' ', line, maxsplit=1)) for line in lines))
        return self
