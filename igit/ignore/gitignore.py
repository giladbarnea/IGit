from typing import Any, List, Callable, Generator

from igit import prompt
from igit.util import cachedprop, termcolor
from igit.util.path import ExPath


class Gitignore:
    def __init__(self):
        self.file = ExPath('.gitignore')
    
    def __getitem__(self, item):
        return self.paths[item]
    
    def __contains__(self, item):
        path = ExPath(item)
        for ignored in self.paths:
            if ignored == path:
                return True
    
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            # support all ExPath methods
            return getattr(self.file, name)
    
    @cachedprop
    def paths(self) -> List[ExPath]:
        with self.file.open(mode='r') as file:
            data = file.read()
        lines = data.splitlines()
        paths = [ExPath(x) for x in lines if bool(x) and '#' not in x]
        return [*paths, ExPath('.git')]
    
    def should_be_ignored(self, p: ExPath, quiet=False) -> bool:
        for ignored in self.paths:
            if ignored == p:
                if not quiet:
                    print(termcolor.yellow(f'{p} already in gitignore, continuing'))
                return False
            if ignored.parent_of(p):
                if quiet:
                    return False
                msg = termcolor.yellow(f"parent '{ignored}' of '{p}' already in gitignore")
                key, action = prompt.action(msg, 'skip', 'ignore anyway', 'debug')
                if action == 'skip':
                    print('skipping')
                    return False
        return True
    
    def write(self, paths, *, confirm=False, dry_run=False):
        writelines = []
        for p in filter(self.should_be_ignored, paths):
            to_write = f'\n{p}'
            if confirm and not prompt.ask(f'ignore {to_write}?'):
                continue
            print(termcolor.green(f'Adding {p} to .gitignore. dry_run={dry_run}'))
            writelines.append(to_write)
        if not dry_run:
            with self.file.open(mode='a') as file:
                file.write(''.join(sorted(writelines)))
    
    def is_subpath_of_ignored(self, p) -> bool:
        path = ExPath(p)
        for ignored in self.paths:
            if ignored.parent_of(path):
                return True
    
    def is_ignored(self, p) -> bool:
        """Returns True if `p` in .gitignore, or `p` is a subpath of a path in .gitignore"""
        path = ExPath(p)
        for ignored in self.paths:
            if ignored == path:
                return True
            if ignored.parent_of(path):
                return True
        return False
    
    def paths_where(self, predicate: Callable[[Any], bool]) -> Generator[ExPath, None, None]:
        for ignored in self.paths:
            if predicate(ignored):
                yield ignored

# g = Gitignore()
# print(g.absolute())
