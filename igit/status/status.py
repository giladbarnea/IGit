import os
from pathlib import Path
from typing import Tuple, List, Dict

from igit.util.types import PathOrStr
from igit.util import shell, termcolor
from igit import prompt
from igit.util.search import search_and_prompt


class Status:
    _status = ''
    _files = []
    _file_status_map = dict()
    
    def __getitem__(self, item) -> List[PathOrStr]:
        # TODO: account for deleted
        try:
            if ':' in item:
                start, _, stop = item.partition(':')
                index = slice(int(start), int(stop))
                return self.files[index]
            else:
                index = int(item)
                return [self.files[index]]
        except ValueError as e:  # not an index
            return [self.search(item)]
    
    def __bool__(self):
        return bool(self.status)
    
    @property
    def status(self) -> List[str]:
        if not self._status:
            self._status = shell.tryrun('git status -s', printout=False, printcmd=False).splitlines()
        return self._status
    
    @property
    def file_status_map(self) -> Dict[Path, str]:
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
        with_slash = '/' in keyword
        print(f'with_suffix: {with_suffix}', f'with_slash: {with_slash}')
        if with_suffix:
            files = self.files
        else:
            files = [f.with_suffix('') for f in self.files]
        """names = [f.name for f in files]
        ## Basenames
        print(termcolor.yellow(f"looking in basenames {'with' if with_suffix else 'without'} suffixes..."))
        try:
            choice = git.search(keyword, names, criterion='equals')
            if choice:
                return choice
        except ValueError as e:
            if 'duplicate' not in e.args[0].lower():
                raise e
            # if duplicate options, continue to search in full paths"""
        
        ## Full Paths
        
        print(termcolor.yellow(f"looking in full paths {'with' if with_suffix else 'without'} suffixes..."))
        for f in files:
            # TODO: integrate into git.search somehow
            for i, part in enumerate(f.parts):
                if part == keyword:
                    return Path(os.path.join(*f.parts[0:i + 1]))
        choice = search_and_prompt(keyword, [str(f) for f in files], criterion='equals')
        if choice:
            return choice
        print(termcolor.red(f"'{keyword}' didn't match anything :/"))
        prompt.generic('debug?', special_opts=('debug', 'quit'))
