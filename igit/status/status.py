import os

from typing import Tuple, List, Dict

from igit.util.misc import try_convert_to_slice, darkprint
from igit.util.path import ExPath, ExPathOrStr, has_file_suffix
from igit.util import shell, cachedprop, search, regex
from igit import prompt
from igit.util.search import search_and_prompt
from more_termcolor import colors
import re


class Status:
    _status = ''
    _files = []
    _file_status_map = dict()
    
    def __getitem__(self, item) -> List[ExPathOrStr]:
        # TODO: account for deleted
        try:
            slyce = try_convert_to_slice(item)
            return self.files[slyce]
        except ValueError as e:  # not an index
            return [self.search(item)]
    
    def __contains__(self, file):
        if file in self.files:
            return True
        path = ExPath(file)
        if path.name == path:
            # it's a basename, simply doesn't exist in status
            return False
        if path.name in self.files:
            return True
        return False
        # maybe file is a basename?
    
    def __bool__(self):
        return bool(self.status)
    
    @cachedprop
    def status(self) -> List[str]:
        return shell.runquiet('git status -s').splitlines()
    
    @cachedprop
    def file_status_map(self) -> Dict[ExPath, str]:
        """A dict of e.g. { ExPath : M }"""
        
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
        # if not self._files:
        #     self._files = [*newfiles, *knownfiles]
        # return self._files
    
    def search(self, keyword: str, quiet=True) -> ExPath:
        path = ExPath(keyword)
        has_suffix = has_file_suffix(path)
        has_slash = '/' in keyword
        has_regex = regex.has_regex(keyword)
        darkprint(f'Status.search({repr(keyword)}) | has_suffix: {has_suffix}, has_slash: {has_slash}, has_regex: {has_regex}')
        if has_suffix:
            files = self.files
        else:
            files = [f.with_suffix('') for f in self.files]
        """names = [f.name for f in files]
        ## Basenames
        print(termcolor.yellow(f"looking in basenames {'with' if has_suffix else 'without'} suffixes..."))
        try:
            choice = git.search(keyword, names, criterion='equals')
            if choice:
                return choice
        except ValueError as e:
            if 'duplicate' not in e.args[0].lower():
                raise e
            # if duplicate options, continue to search in full paths"""
        
        if has_regex:
            for f in files:
                if re.search(keyword, f):
                    return ExPath(f)
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
        if quiet:
            return None
        darkprint("didn't find a matching part, calling search_and_prompt(criterion='equals')...")
        choice = search_and_prompt(keyword, [str(f) for f in files], criterion='equals')
        if choice:
            return choice
        print(colors.red(f"'{keyword}' didn't match anything :/"))
        prompt.generic('debug?', flowopts=('debug', 'quit'))
