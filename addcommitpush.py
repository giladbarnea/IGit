#!/usr/bin/env python3.7
from typing import Dict
from mytool import term, util
import os
import click
from pathlib import Path

from mytool import git
from mytool.git.ignore import main as ignore


def verify_shebang(f: Path, lines):
    shebang = '#!/usr/bin/env python3.7'
    firstline = lines[0].splitlines()[0]
    if firstline != shebang:
        answer = util.ask(f"{f} first line invalid shebang ('{firstline.splitlines()[0]}'), put '{shebang}'?", 'add', 'continue', 'ignore', 'quit', 'debug')
        if answer == 'd':
            from pprint import pprint as pp
            from ipdb import set_trace
            import inspect
            set_trace(inspect.currentframe(), context=30)
        elif answer == 'i':
            ignore([str(f)])
        elif answer == 'a':
            with f.open(mode='w') as opened:
                opened.write('\n'.join([shebang] + lines))
                term.green(f'Added shebag to {f.name} successfully')


def handle_large_files(cwd, largepaths: Dict[Path, float]):
    print(term.warn(f'{len(largepaths)} large paths sized >= 30MB found:'))
    for abspath, mbsize in largepaths.items():
        stats = f'{abspath.relative_to(cwd)} ({mbsize}MB)'
        if abspath.is_dir():
            stats += f' ({len(list(abspath.iterdir()))} sub items)'
        print(stats)
    answer = util.ask('Choose:', 'continue', 'ignore', 'quit', 'debug')
    if answer == 'd':
        from pprint import pprint as pp
        from pdbi import set_trace
        import inspect
        set_trace(inspect.currentframe())
    elif answer == 'i':
        ignore([str(p.relative_to(cwd)) for p in largepaths])


def handle_empty_file(f):
    answer = util.ask(f"{f} is new and has no content, what to do?", 'continue', 'ignore', 'quit', 'debug')
    if answer == 'd':
        from pprint import pprint as pp
        from ipdb import set_trace
        import inspect
        set_trace(inspect.currentframe(), context=30)
    elif answer == 'i':
        ignore([str(f)])


@click.command()
@click.argument('commitmsg', required=False)
def main(commitmsg):
    file_status_map = git.file_status_map()
    files = list(file_status_map.keys())
    if not files:
        util.ask('No files in status, just push?')
        return util.tryrun('git push')
    
    cwd = Path(os.getcwd())
    largepaths: Dict[Path, float] = {}
    for f in files:
        status = file_status_map[f]
        if 'D' in status:
            continue
        if ('A' in status
                and f.suffix == '.py'
                and not f.name.startswith('__')
                and cwd == '/Users/gilad/Code/MyTool'):
            with f.open(mode='r+') as opened:
                lines = opened.readlines()
            if not lines:
                handle_empty_file(f)
            else:
                verify_shebang(f, lines)
        
        # populate largepaths
        abspath = cwd / f
        mb = 0
        if abspath.is_dir():
            mb += util.dirsize(abspath) / 1000000
        else:
            mb = abspath.lstat().st_size / 1000000
        if mb >= 30:
            largepaths[abspath] = mb
    if largepaths:
        handle_large_files(cwd, largepaths)
    if not commitmsg:
        if len(files) == 1:
            commitmsg = files[0]
        elif len(files) < 3:
            commitmsg = ', '.join([f.name for f in files])
        else:
            commitmsg = util.removequotes(input('commit msg:\t'))
    util.tryrun('git add .',
                f'git commit -a -m "{commitmsg}"',
                f'git push')


if __name__ == '__main__':
    try:
        main()
    except FileNotFoundError as e:
        print(term.warn(e))
        raise e
