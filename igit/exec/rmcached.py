#!/usr/bin/env python3.8
import os
import sys
import click
from igit import prompt, git
from igit.ignore import Gitignore
from igit.status import Status
from igit.util import termcolor, shell
from igit.util.misc import unquote, try_convert_to_idx
from igit.util.path import ExPath


@click.command()
@click.argument('paths', nargs=-1)
def main(paths):
    print(f'main({", ".join(paths)})')
    # TODO: see if exists in status
    if not paths:
        sys.exit(termcolor.red('no paths! exiting'))
    
    cmds = []
    gitignore = Gitignore()
    status = Status()
    existing_paths = []
    for p in paths:
        try:
            # * maybe index
            converted = try_convert_to_idx(p)
            print(termcolor.lightgrey(f'p: {p}, converted: {converted}'))
            p = status[converted]
        except TypeError as e:
            # * not index, just str
            p = ExPath(unquote(p))
        
        if not p.exists():
            print(f"{termcolor.yellow(p)} does not exist, skipping")
            continue
        
        # exists
        if p.is_dir():
            cmds.append(f'git rm -r --cached {p}')
        else:
            cmds.append(f'git rm --cached {p}')
        
        existing_paths.append(p)
    
    if not cmds:
        sys.exit(termcolor.red('no paths to rm, exiting'))
    
    shell.tryrun(*cmds, raiseonfail=False)
    if prompt.ask(f'try to ignore {len(existing_paths)} paths?'):
        gitignore.ignore(existing_paths)
    
    key, answer = prompt.generic(f'commit and push?', 'yes, commit with "Removed from cache: ..."', 'custom commit message', 'quit')
    if key == 'y':
        commitmsg = f'Removed from cache: ' + ', '.join(map(str, paths))
    else:
        commitmsg = prompt.generic('commit msg:', allow_free_input=True)[1]
    shell.tryrun(f'git commit -a -m "{commitmsg}"')
    git.push()


if __name__ == '__main__':
    main()
