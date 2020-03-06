#!/usr/bin/env python3.7
from mytool import util
import click
import sys
import os

from mytool import git


@click.command()
@click.argument('name')
def main(name):
    branches = git.branch.getall()
    if name in branches:
        if not util.ask(f'"{name}" already exists, check it out?'):
            sys.exit()
        util.tryrun(f'git checkout {name}')
        return os.system('git pull')
    
    status = git.shortstatus()
    stash = False
    if status:
        os.system('git status')
        answer = util.ask('Uncommitted changes', 'stash => apply', 'continue checkout', 'quit')
        if answer == 's':
            stash = True
            util.tryrun('git stash')
        elif answer == 'c':
            stash = False
    util.tryrun(f'git checkout -b {name}',
                f'git push --set-upstream origin {name}')
    if stash:
        util.tryrun('git stash apply', 'git push')


if __name__ == '__main__':
    main()
