#!/usr/bin/env python3.7
from typing import Dict
from mytool import term, util
import os
import click
from pathlib import Path

from mytool import git, prompt
from mytool.git.ignore import main as ignore


def verify_shebang(f: Path, lines):
    shebang = '#!/usr/bin/env python3.7'
    firstline = lines[0].splitlines()[0]
    if firstline != shebang:
        # answer = util.ask(f"{f} first line invalid shebang ('{firstline.splitlines()[0]}'), put '{shebang}'?", 'add', 'ignore', 'continue', 'debug', 'quit')
        answer = prompt.action(f"{f} first line invalid shebang ('{firstline.splitlines()[0]}'), put '{shebang}'?", 'add', 'ignore', special_opts=True)
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
    answer = prompt.action('Choose:', 'ignore', special_opts=True)
    if answer == 'd':
        from pprint import pprint as pp
        from ipdb import set_trace
        import inspect
        set_trace(inspect.currentframe(), context=50)
    elif answer == 'i':
        ignore([str(p.relative_to(cwd)) for p in largepaths])


def handle_empty_file(f):
    answer = util.ask(f"{f} is new and has no content, what to do?", 'ignore', 'continue', 'debug', 'quit')
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
    status = git.status()
    if not status.files:
        util.ask('No files in status, just push?')
        return util.tryrun('git push')
    
    cwd = Path(os.getcwd())
    largepaths: Dict[Path, float] = {}
    for f in status.files:
        statuce = status.file_status_map[f]
        if 'D' in statuce:
            continue
        if ('A' in statuce
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
        if len(status.files) == 1:
            commitmsg = status.files[0]
        elif len(status.files) < 3:
            commitmsg = ', '.join([f.name for f in status.files])
        else:
            commitmsg = input('commit msg:\t')
    commitmsg = util.removequotes(commitmsg)
    util.tryrun('git add .',
                f'git commit -am "{commitmsg}"',
                f'git push')


if __name__ == '__main__':
    try:
        main()
    except FileNotFoundError as e:
        print(term.warn(e))
        raise e
