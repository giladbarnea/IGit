from typing import Any, List

from igit import prompt
from igit.util import cachedprop, termcolor
from igit.util.path import ExPath


class Gitignore:
    def __init__(self):
        self.file = ExPath('.gitignore')
    
    def __getitem__(self, item):
        return self.paths[item]
    
    @cachedprop
    def paths(self):
        with self.file.open(mode='r') as file:
            data = file.read()
        lines = data.splitlines()
        paths = [ExPath(x) for x in filter(bool, lines)]
        return paths
    
    def _should_be_ignored(self, p: ExPath):
        for ignored in self.paths:
            if ignored == p:
                print(termcolor.yellow(f'{p} already in gitignore, continuing'))
                return False
            if ignored.parent_of(p):
                msg = termcolor.yellow(f"parent '{ignored}' of '{p}' already in gitignore")
                key, action = prompt.action(msg, 'skip', 'ignore anyway', 'debug')
                if action == 'skip':
                    print('skipping')
                    return False
        return True
    
    def ignore(self, paths, *, confirm=False, dry_run=False):
        writelines = []
        for p in filter(self._should_be_ignored, paths):
            to_write = f'\n{p}'
            if confirm and not prompt.ask(f'ignore {to_write}?'):
                continue
            print(termcolor.green(f'Adding {p} to .gitignore. dry_run={dry_run}'))
            writelines.append(to_write)
        if not dry_run:
            with self.file.open(mode='a') as file:
                file.write(''.join(sorted(writelines)))
    
    def is_ignored(self, p):
        return bool(self.paths_where(lambda ignored: ignored == p))
    
    def is_subpath_of_ignored(self, p):
        return bool(self.paths_where(lambda ignored: ignored.parent_of(p)))
    
    def paths_where(self, predicate) -> List[ExPath]:
        truthies = []
        for ignored in self.paths:
            if predicate(ignored):
                truthies.append(ignored)
        return truthies
    
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            # support all ExPath methods
            return getattr(self.file, name)

# g = Gitignore()
# print(g.absolute())
