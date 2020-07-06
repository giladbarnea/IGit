import re
from typing import Any, List, Callable, Generator

from igit.util.cache import memoize
from more_termcolor import colors

from igit import prompt
from igit.util import shell
from igit.util.misc import yellowprint, brightyellowprint, greenprint, darkprint
from igit.util.path import ExPath
from igit_debug.loggr import Loggr

logger = Loggr(__name__)


class Gitignore:
    # https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository#Ignoring-Files
    def __init__(self):
        self.file = ExPath('.gitignore')
        if not self.file.is_file():
            raise FileNotFoundError(f'Gitignore.__init__(): {self.file.absolute()} is not a file')
    
    def __getitem__(self, item):
        return self.values[item]
    
    def __contains__(self, item):
        path = ExPath(item)
        for ignored in self:
            if ignored == path:
                return True
        return False
    
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            # support all ExPath methods
            return getattr(self.file, name)
    
    def __iter__(self):
        yield from self.values
    
    # @cachedprop # TODO: uncomment when possible to clear cache
    @property
    @memoize
    def values(self) -> List[ExPath]:
        with self.file.open(mode='r') as file:
            data = file.read()
        lines = data.splitlines()
        paths = []
        for x in lines:
            if not bool(x) or '#' in x:
                continue
            paths.append(ExPath(x))
        return [*paths, ExPath('.git')]
    
    def should_add_to_gitignore(self, p: ExPath, quiet=False) -> bool:
        for ignored in self.values:
            if ignored == p:
                if not quiet:
                    yellowprint(f'{p} already in gitignore, continuing')
                return False
            logger.debug(f'ignored:', ignored, 'p:', p, types=True)
            if ignored.parent_of(p):
                if quiet:
                    return False
                msg = colors.yellow(f"parent '{ignored}' of '{p}' already in gitignore")
                key, action = prompt.action(msg, 'skip', 'ignore anyway', flowopts=('debug', 'quit'))
                if action.value == 'skip':
                    print('skipping')
                    return False
        return True
    
    def backup(self, confirm: bool):
        if confirm and not prompt.confirm(f'Backup .gitignore to .gitignore.backup?'):
            print('aborting')
            return False
        absolute = self.file.absolute()
        
        try:
            shell.run(f'cp {absolute} {absolute}.backup', raiseonfail='summary')
        except Exception as e:
            if not prompt.confirm('Backup failed, overwrite .gitignore anyway?', flowopts='debug'):
                print('aborting')
                return False
            return True
        else:
            backup = ExPath(f'{absolute}.backup')
            if not backup.exists() and not prompt.confirm(f'Backup command completed without error, but {backup} doesnt exist. overwrite .gitignore anyway?', flowopts='debug'):
                print('aborting')
                return False
            return True
    
    def unignore(self, path, *, confirm=False, dry_run=False, backup=True):
        # TODO: this is not working
        raise NotImplementedError
        # noinspection PyUnreachableCode
        path = ExPath(path)
        if path not in self:
            brightyellowprint(f'Gitignore.unignore(path={path}): not in self. returning')
            return
        if confirm and not prompt.confirm(f'Remove {path} from .gitignore?'):
            print('aborting')
            return
        if dry_run:
            print('dry_run, returning')
            return
        self.write([p for p in self.values if p != path], backup=backup)
    
    def write(self, paths, *, confirm=False, dry_run=False, backup=True):
        logger.debug(f'paths:', paths, 'confirm:', confirm, 'dry_run:', dry_run, 'backup:', backup)
        writelines = []
        for p in filter(self.should_add_to_gitignore, paths):
            to_write = f'\n{p}'
            if confirm and not prompt.confirm(f'Add {p} to .gitignore?'):
                continue
            greenprint(f'Adding {p} to .gitignore. dry_run={dry_run}')
            writelines.append(to_write)
        if dry_run:
            print('dry_run, returning')
            return
        if backup:
            backup_ok = self.backup(confirm)
            if not backup_ok:
                return
        
        with self.file.open(mode='a') as file:
            file.write(''.join(sorted(writelines)))
        Gitignore.values.fget.clear_cache()
        
        # TODO: reset cached self.values
    
    def is_subpath_of_ignored(self, p) -> bool:
        """Returns True if `p` is strictly a subpath of a path in .gitignore"""
        path = ExPath(p)
        for ignored in self:
            if ignored.parent_of(path):
                return True
        return False
    
    def is_ignored(self, p) -> bool:
        """Returns True if `p` in .gitignore, or if `p` is a subpath of a path in .gitignore,
        or if `p` fullmatches any part of a path in .gitignore (i.e. if 'env' is ignored, then 'src/env' returns True)"""
        path = ExPath(p)
        for ignored in self:
            if ignored == path:
                return True
            if ignored.parent_of(path):
                return True
            if any(re.fullmatch('env', part) for part in path.parts):
                return True
        return False
    
    def paths_where(self, predicate: Callable[[Any], bool]) -> Generator[ExPath, None, None]:
        for ignored in self:
            if predicate(ignored):
                yield ignored

# g = Gitignore()
# print(g.absolute())
