import os

from typing import Tuple, List, Dict

from igit.util.misc import try_convert_to_slice
from igit.util.path import ExPath as Path
from igit.util.types import PathOrStr
from igit.util import shell, termcolor, cachedprop
from igit import prompt
from igit.util.search import search_and_prompt


class Status:
    _status = ''
    _files = []
    _file_status_map = dict()
    
    def __getitem__(self, item) -> List[PathOrStr]:
        # TODO: account for deleted
        try:
            slyce = try_convert_to_slice(item)
            return self.files[slyce]
        except ValueError as e:  # not an index
            return [self.search(item)]
    
    def __bool__(self):
        return bool(self.status)
    
    @cachedprop
    def status(self) -> List[str]:
        return shell.tryrun('git status -s', printout=False, printcmd=False).splitlines()
    
    @cachedprop
    def file_status_map(self) -> Dict[Path, str]:
        def _clean_shortstatus(_x) -> Tuple[Path, str]:
            # _file, _status = _x[3:].replace('"', ''), _x[:3].strip()
            _status, _file = map(str.strip, _x.split(maxsplit=1))
            if 'R' in _status:
                if '->' not in _file:
                    raise ValueError(f"'R' in status but '->' not in file. file: {_file}, status: {_status}", locals())
                _, _, _file = _file.partition(' -> ')  # return only existing
            else:
                if '->' in _file:
                    raise ValueError(f"'R' not in status but '->' in file. file: {_file}, status: {_status}", locals())
            return Path(_file), _status
        
        return dict([_clean_shortstatus(s) for s in self.status])
    
    @cachedprop
    def files(self) -> List[Path]:
        newfiles = []
        knownfiles = []
        for file, statuce in self.file_status_map.items():
            if 'A' in statuce:
                newfiles.append(file)
            else:
                knownfiles.append(file)
        return [*newfiles, *knownfiles]
        # if not self._files:
        #     self._files = [*newfiles, *knownfiles]
        # return self._files
    
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
