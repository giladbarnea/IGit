from mytool import util, term, git
from typing import Tuple, List, Optional
import re
from pathlib import Path


class status:
    _status = ''
    _files = []
    _file_status_map = dict()
    
    @property
    def status(self) -> List[str]:
        if not self._status:
            self._status = util.tryrun('git status -s', printout=False, printcmd=False).splitlines()
        return self._status
    
    @property
    def file_status_map(self):
        def _clean_shortstatus(_x) -> Tuple[Path, str]:
            _file, _status = _x[3:].replace('"', ''), _x[:3].strip()
            if 'R' in _status:
                if '->' not in _file:
                    raise ValueError(f"'R' in status but '->' not in file. file: {_file}, status: {_status}", locals())
                _, _, _file = _file.partition(' -> ')  # return only existing
            else:
                if '->' in _file:
                    raise ValueError(f"'R' not in status but '->' in file. file: {_file}, status: {_status}", locals())
            return Path(_file), _status
        
        if not self._file_status_map:
            self._file_status_map = self._file_status_map = dict([_clean_shortstatus(s) for s in self.status])
        return self._file_status_map
    
    @property
    def files(self) -> List[Path]:
        if not self._files:
            newfiles = []
            knownfiles = []
            for file, statuce in self.file_status_map.items():
                if 'A' in statuce:
                    newfiles.append(file)
                else:
                    knownfiles.append(file)
            self._files = [*newfiles, *knownfiles]
        return self._files
    
    def search(self, keyword: str) -> str:
        with_suffix = bool(Path(keyword).suffix)
        if with_suffix:
            files = self.files
        else:
            files = [f.with_suffix('') for f in self.files]
        """names = [f.name for f in files]
        ## Basenames
        print(term.warn(f"looking in basenames {'with' if with_suffix else 'without'} suffixes..."))
        try:
            choice = git.search(keyword, names, criterion='equals')
            if choice:
                return choice
        except ValueError as e:
            if 'duplicate' not in e.args[0].lower():
                raise e
            # if duplicate options, continue to search in full paths"""
        
        ## Full Paths
        print(term.warn(f"looking in full paths {'with' if with_suffix else 'without'} suffixes..."))
        choice = git.search(keyword, [str(f) for f in self.files], criterion='equals')
        if choice:
            return choice
        print(term.red(f"'{keyword}' didn't match anything :/"))
        util.ask('debug?', 'debug', 'quit')
