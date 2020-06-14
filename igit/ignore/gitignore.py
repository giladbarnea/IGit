from typing import Any, List, Callable, Generator

from igit import prompt
from igit.util import cachedprop
from igit.util.path import ExPath
from more_termcolor import colors


class Gitignore:
    def __init__(self):
        self.file = ExPath('.gitignore')
    
    def __getitem__(self, item):
        return self.values[item]
    
    def __contains__(self, item):
        path = ExPath(item)
        for ignored in self.values:
            if ignored == path:
                return True
    
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            # support all ExPath methods
            return getattr(self.file, name)
    
    @cachedprop
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
                    print(colors.yellow(f'{p} already in gitignore, continuing'))
                return False
            if ignored.parent_of(p):
                if quiet:
                    return False
                msg = colors.yellow(f"parent '{ignored}' of '{p}' already in gitignore")
                key, action = prompt.action(msg, 'skip', 'ignore anyway', special_ops='debug')
                if action == 'skip':
                    print('skipping')
                    return False
        return True
    
    def write(self, paths, *, confirm=False, dry_run=False):
        writelines = []
        for p in filter(self.should_add_to_gitignore, paths):
            to_write = f'\n{p}'
            if confirm and not prompt.confirm(f'Add {p} to .gitignore?'):
                continue
            print(colors.green(f'Adding {p} to .gitignore. dry_run={dry_run}'))
            writelines.append(to_write)
        if not dry_run:
            with self.file.open(mode='a') as file:
                file.write(''.join(sorted(writelines)))
    
    def is_subpath_of_ignored(self, p) -> bool:
        path = ExPath(p)
        for ignored in self.values:
            if ignored.parent_of(path):
                return True
    
    def is_ignored(self, p) -> bool:
        """Returns True if `p` in .gitignore, or `p` is a subpath of a path in .gitignore"""
        path = ExPath(p)
        for ignored in self.values:
            if ignored == path:
                return True
            if ignored.parent_of(path):
                return True
        return False
    
    def paths_where(self, predicate: Callable[[Any], bool]) -> Generator[ExPath, None, None]:
        for ignored in self.values:
            if predicate(ignored):
                yield ignored

# g = Gitignore()
# print(g.absolute())
