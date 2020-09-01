import re
from typing import Any, List, Callable, Generator

from igit_debug.loggr import Loggr
from more_termcolor import colors

from igit import prompt, shell
from igit.util.cache import memoize
from igit.expath import ExPath

logger = Loggr(__name__)
WORD_RE = re.compile('\w')


class Gitignore:
    # https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository#Ignoring-Files
    def __init__(self):
        self.file = ExPath('.gitignore')
        if not self.file.exists():
            raise FileNotFoundError(f'Gitignore.__init__(): {self.file.absolute()} does not exist')
    
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
            if not bool(x) or '#' in x or not WORD_RE.search(x):
                continue
            paths.append(ExPath(x))
        return [*paths, ExPath('.git')]
    
    def should_add_to_gitignore(self, p: ExPath, quiet=False) -> bool:
        for ignored in self.values:
            if ignored == p:
                if not quiet:
                    logger.warn(f'{p} already in gitignore, continuing')
                return False
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
            shell.run(f'cp {absolute} {absolute}.backup', raiseexc='summary')
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
    
    def write(self, paths, *, verify_paths=True, confirm=False, dry_run=False, backup=True):
        logger.debug(f'paths:', paths, 'verify_paths:', verify_paths, 'confirm:', confirm, 'dry_run:', dry_run, 'backup:', backup)
        writelines = []
        if verify_paths:
            should_add_to_gitignore = self.should_add_to_gitignore
        else:
            should_add_to_gitignore = lambda p: True
        for p in filter(should_add_to_gitignore, paths):
            to_write = f'\n{p}'
            if confirm and not prompt.confirm(f'Add {p} to .gitignore?'):
                continue
            logger.good(f'Adding {p} to .gitignore. dry_run={dry_run}, backup={backup}, confirm={confirm}')
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
    
    def unignore(self, path, *, confirm=False, dry_run=False, backup=True):
        path = ExPath(path)
        newvals = []
        found = False
        for ignored in self:
            if ignored == path:
                breakpoint()
                found = True
                continue
            newvals.append(ignored)
        if not found:
            logger.boldwarn(f'Gitignore.unignore(path={path}): not in self. returning')
            return
        
        if confirm and not prompt.confirm(f'Remove {path} from .gitignore?'):
            print('aborting')
            return
        self.write(newvals, verify_paths=False, dry_run=dry_run, backup=backup)
    
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
