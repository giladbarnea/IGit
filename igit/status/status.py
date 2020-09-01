import os

from typing import Tuple, List, Dict, overload, Union

from igit.util.misc import darkprint
from igit.util.path import ExPath, has_file_suffix
from igit.util import cachedprop, search, regex, misc
from igit import prompt, shell
from igit.util.search import search_and_prompt
from more_termcolor import colors
import re


class Status:
    """status[1:3], status["1:3"] → [ExPath, ExPath]
    status[1], status["1"] → ExPath
    status[".gitignore"], status[ExPath('.gitignore')] → 'M'
    """
    # TODO: HybridList (because __getitem__ returns 'keys')
    _status = ''
    _files: List[ExPath] = []
    _file_status_map: Dict[ExPath, str] = dict()
    
    @overload
    def __getitem__(self, k: slice) -> List[ExPath]:
        """status[1:3] → [ExPath, ExPath]"""
        ...
    
    @overload
    def __getitem__(self, k: str) -> Union[ExPath, List[ExPath], str]:
        """If `k` is a number, returns ExPath.
        If `k` is slice-like, returns list of ExPaths.
        if `k` is path-like, returns the file's status (str).
        status["1"] → ExPath
        status["1:3"] → [ExPath, ExPath]
        status[".gitignore"] → 'M'
        """
        ...
    
    @overload
    def __getitem__(self, k: int) -> ExPath:
        """status[1] → ExPath"""
        ...
    
    @overload
    def __getitem__(self, k: ExPath) -> str:
        """Returns the file's status (str).
        status[ExPath('.gitignore')] → 'M'
        """
        ...
    
    def __getitem__(self, k):
        nothing = object()
        retrieved = self.get(k, nothing)
        if retrieved is nothing:
            raise
        return retrieved
    
    def get(self, k, default=None, *, noprompt=True):
        try:
            idx = misc.safeint(k)
            if idx is not None:
                return self.files[idx]
            slyce = misc.safeslice(k)
            if slyce is not None:
                sliced = self.files[slyce]
                return sliced
            if isinstance(k, (str, ExPath)):
                for f in self.files:
                    if f == k:
                        return self.file_status_map[f]
            
            return self.search(k, noprompt=noprompt)
        except (IndexError, KeyError) as e:
            return default
    
    def __contains__(self, file):
        for f in self.files:
            if f == file:
                return True
        return False
    
    def __bool__(self):
        return bool(self.status)
    
    def __repr__(self) -> str:
        os.system('git status -s')
        return super().__repr__()
    
    @cachedprop
    def status(self) -> List[str]:
        return shell.runquiet('git status -s').splitlines()
    
    @cachedprop
    def file_status_map(self) -> Dict[ExPath, str]:
        """A dict of e.g. { ExPath : 'M' }"""
        
        def _clean_shortstatus(_x) -> Tuple[ExPath, str]:
            # _file, _status = _x[3:].replace('"', ''), _x[:3].strip()
            _status, _file = map(str.strip, _x.split(maxsplit=1))
            if 'R' in _status:
                if '->' not in _file:
                    raise ValueError(f"'R' in status but '->' not in file. file: {_file}, status: {_status}", locals())
                _, _, _file = _file.partition(' -> ')  # return only existing
            else:
                if '->' in _file:
                    raise ValueError(f"'R' not in status but '->' in file. file: {_file}, status: {_status}", locals())
            return ExPath(_file), _status
        
        return dict([_clean_shortstatus(s) for s in self.status])
    
    @cachedprop
    def files(self) -> List[ExPath]:
        """An ExPath list of files appearing in git status"""
        newfiles = []
        knownfiles = []
        for file, statuce in self.file_status_map.items():
            if 'A' in statuce:
                newfiles.append(file)
            else:
                knownfiles.append(file)
        return [*newfiles, *knownfiles]
    
    def search(self, keyword: Union[str, ExPath], *, noprompt=True) -> ExPath:
        """Tries to return an ExPath in status.
         First assumes `keyword` is an exact file (str or ExPath), and if fails, uses `search` module.
         @param noprompt: specify False to allow using search_and_prompt(keyword, file) in case nothing matched earlier.
         """
        darkprint(f'Status.search({repr(keyword)}) |')
        path = ExPath(keyword)
        for file in self.files:
            if file == path:
                return file
        has_suffix = has_file_suffix(path)
        has_slash = '/' in keyword
        has_regex = regex.has_regex(keyword)
        darkprint(f'\thas_suffix: {has_suffix}, has_slash: {has_slash}, has_regex: {has_regex}')
        if has_suffix:
            files = self.files
        else:
            files = [f.with_suffix('') for f in self.files]
        
        if has_regex:
            for expath in files:
                if re.search(keyword, str(expath)):
                    return expath
        if has_slash:
            darkprint(f"looking for the nearest match among status paths for: '{keyword}'")
            return ExPath(search.nearest(keyword, files))
        darkprint(f"looking for a matching part among status paths ({'with' if has_suffix else 'without'} suffixes...) for: '{keyword}'")
        for f in files:
            # TODO: integrate into git.search somehow
            for i, part in enumerate(f.parts):
                if part == keyword:
                    ret = ExPath(os.path.join(*f.parts[0:i + 1]))
                    return ret
        if noprompt:
            return None
        darkprint(f"didn't find a matching part, calling search_and_prompt()...")
        choice = search_and_prompt(keyword, [str(f) for f in files], criterion='substring')
        if choice:
            return ExPath(choice)
        
        prompt.generic(colors.red(f"'{keyword}' didn't match anything"), flowopts=True)
