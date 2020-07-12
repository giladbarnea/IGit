#!/usr/bin/env python3.8
import os
import sys
import click
from igit import prompt, git
from igit.ignore import Gitignore
from igit.status import Status
from igit.util import shell
from igit.util.misc import unquote
from igit.util.path import ExPath
from more_termcolor import colors


@click.command()
@click.argument('paths', nargs=-1)
def main(paths):
    print(f'main({", ".join(paths)})')
    # TODO: see if exists in status
    if not paths:
        sys.exit(colors.red('no values! exiting'))
    
    cmds = []
    gitignore = Gitignore()
    status = Status()
    existing_paths = []
    for p in paths:
        try:
            # * maybe index
            p = status[p]
        except TypeError as e:
            # * not index, just str
            p = ExPath(unquote(p))
        
        if not p.exists():
            print(f"{colors.yellow(p)} does not exist, skipping")
            continue
        
        # exists
        if p.is_dir():
            cmds.append(f'git rm -r --cached {p}')
        else:
            cmds.append(f'git rm --cached {p}')
        
        existing_paths.append(p)
    
    if not cmds:
        sys.exit(colors.red('no values to rm, exiting'))
    
    shell.run(*cmds, raiseonfail=False)
    if prompt.confirm(f'try to ignore {len(existing_paths)} values?'):
        gitignore.write(existing_paths)
    
    commitmsg = f'Removed from cache: ' + ', '.join(map(str, paths))
    answer = prompt.generic(f'commit and push?', f'yes, commit with "{commitmsg}"', 'custom commit message', flowopts='quit')
    if answer is not True:
        commitmsg = prompt.generic('commit msg:', free_input=True)[1]
    shell.run(f'git commit -am "{commitmsg}"')
    git.push()


if __name__ == '__main__':
    main()
