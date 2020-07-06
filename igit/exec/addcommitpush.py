#!/usr/bin/env python3.8
import os
import re
from pathlib import Path
from typing import Dict

import click

from igit import git, prompt, util
from igit.exec.ignore import main as ignore
from igit.status import Status
from igit.util import shell, misc
from more_termcolor import colors, cprint


def verify_shebang(f: Path, lines):
    regex = re.compile(r'^#!/usr/bin/env python3\.([78])$')
    firstline = lines[0].splitlines()[0]
    if not re.fullmatch(regex, firstline):
        raise NotImplementedError()
        # noinspection PyUnreachableCode
        answer = prompt.action(f"{f} first line invalid shebang ('{firstline.splitlines()[0]}')",
                               'add to .gitignore', 'add python3.7 shebang', 'add python3.8 shebang',
                               flowopts=True)
        
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
                print(colors.green(f'Added shebag to {f.name} successfully'))


def handle_large_files(cwd, largepaths: Dict[Path, float]):
    cprint(f'{len(largepaths)} large paths sized >= 30MB found:', 'bright yellow')
    for abspath, mbsize in largepaths.items():
        stats = f'{abspath.relative_to(cwd)} ({mbsize}MB)'
        if abspath.is_dir():
            stats += f' ({len(list(abspath.iterdir()))} sub items)'
        print(stats)
    key, answer = prompt.action('What to do?', 'ignore all', 'skip all', 'choose individually', flowopts=True)
    if key == 'i':
        ignore([p.relative_to(cwd) for p in largepaths])


def handle_empty_file(f):
    key, answer = prompt.action(f"{f} is new and has no content, what to do?", 'ignore', flowopts=True)
    if answer == 'i':
        ignore([str(f)])


@click.command()
@click.argument('commitmsg', required=False)
def main(commitmsg: str):
    status = Status()
    if not status.files:
        if prompt.confirm('No files in status, just push?'):
            return git.push()
    
    cwd = Path(os.getcwd())
    largepaths: Dict[Path, float] = {}
    for f in status.files:
        statuce = status.file_status_map[f]
        if 'D' in statuce:
            continue
        # if ('A' in statuce
        #         and f.suffix == '.py'
        #         and not f.name.startswith('__')
        #         and cwd == '/home/gilad/Code/MyTool'):
        #     with f.open(mode='r+') as opened:
        #         lines = opened.readlines()
        #     if not lines:
        #         handle_empty_file(f)
        #     else:
        #         verify_shebang(f, lines)
        # TODO: check if already in gitignore and just not removed from cache
        # populate largepaths
        abspath = cwd / f
        mb = 0
        if abspath.exists():
            if abspath.is_dir():
                mb = util.path.dirsize(abspath) / 1000000
            else:
                mb = abspath.lstat().st_size / 1000000
        else:
            cprint(f'does not exist: {repr(abspath)}', 'yellow')
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
            os.system('git status -s')
            commitmsg = input('commit msg:\t')
    commitmsg = misc.unquote(commitmsg)
    
    shell.run('git add .',
              f'git commit -am "{commitmsg}"')
    git.push()


if __name__ == '__main__':
    try:
        main()
    except FileNotFoundError as e:
        print(colors.brightred(repr(e)))
        raise e
