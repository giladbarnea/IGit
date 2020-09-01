#!/usr/bin/env python3.8
import sys

import click
from more_termcolor import colors

from igit import prompt, git, shell
from igit.ignore import Gitignore
from igit.status import Status
from igit.util.misc import yellowprint


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
        breakpoint()
        path = status.search(p, noprompt=False)
        if not path:
            yellowprint(f"status.search({p}) return None, skipping")
            continue
        if not path.exists():
            yellowprint(f"{p} does not exist, skipping")
            continue
        
        # exists
        if path.is_dir():
            cmds.append(f'git rm -r --cached {path}')
        else:
            cmds.append(f'git rm --cached {path}')
        
        existing_paths.append(path)
    
    if not cmds:
        sys.exit(colors.red('no values to rm, exiting'))
    
    shell.run(*cmds, raiseexc=False)
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
