#!/usr/bin/env python3.8
import os
import re
from pathlib import Path
from typing import Dict

import click

import git
import prompt
import util
from exec.ignore import main as ignore
from status import Status
from util import shell, termcolor, misc


def verify_shebang(f: Path, lines):
    regex = re.compile(r'^#!/usr/bin/env python3\.([78])$')
    firstline = lines[0].splitlines()[0]
    if not re.fullmatch(regex, firstline):
        answer = prompt.choose(f"{f} first line invalid shebang ('{firstline.splitlines()[0]}')",
                               'add to .gitignore', 'add python3.7 shebang', 'add python3.8 shebang',
                               special_opts=True)
        
        if answer == '0':
            ignore([f])
            return
        if answer in ('1', '2'):
            shebang = '/usr/bin/env python3.'
            if answer == '1':
                shebang += '7'
            else:
                shebang += '8'
            with f.open(mode='w') as opened:
                opened.write('\n'.join([shebang] + lines))
                print(termcolor.green(f'Added shebag to {f.name} successfully'))


def handle_large_files(cwd, largepaths: Dict[Path, float]):
    print(termcolor.yellow(f'{len(largepaths)} large paths sized >= 30MB found:'))
    for abspath, mbsize in largepaths.items():
        stats = f'{abspath.relative_to(cwd)} ({mbsize}MB)'
        if abspath.is_dir():
            stats += f' ({len(list(abspath.iterdir()))} sub items)'
        print(stats)
    answer = prompt.action('Choose:', 'ignore', special_opts=True)
    if answer == 'i':
        ignore([p.relative_to(cwd) for p in largepaths])


def handle_empty_file(f):
    answer = prompt.action(f"{f} is new and has no content, what to do?", 'ignore', special_opts=True)
    if answer == 'd':
        from ipdb import set_trace
        import inspect
        set_trace(inspect.currentframe(), context=50)
    elif answer == 'i':
        ignore([str(f)])


@click.command()
@click.argument('commitmsg', required=False)
def main(commitmsg: str):
    status = Status()
    if not status.files:
        if prompt.ask('No files in status, just push?'):
            return git.push()
    
    cwd = Path(os.getcwd())
    largepaths: Dict[Path, float] = {}
    for f in status.files:
        statuce = status.file_status_map[f]
        if 'D' in statuce:
            continue
        if ('A' in statuce
                and f.suffix == '.py'
                and not f.name.startswith('__')
                and cwd == '/home/gilad/Code/MyTool'):
            with f.open(mode='r+') as opened:
                lines = opened.readlines()
            if not lines:
                handle_empty_file(f)
            else:
                verify_shebang(f, lines)
        # TODO: check if already in gitignore and just not removed from cache
        # populate largepaths
        abspath = cwd / f
        mb = 0
        if abspath.is_dir():
            mb += util.path.dirsize(abspath) / 1000000
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
    commitmsg = misc.unquote(commitmsg)
    shell.tryrun('sudo git add .',
                 f'sudo git commit -am "{commitmsg}"')
    git.push()


if __name__ == '__main__':
    try:
        main()
    except FileNotFoundError as e:
        print(termcolor.yellow(e))
        raise e
