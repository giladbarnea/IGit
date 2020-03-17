#!/usr/bin/env python3.7
import click
import sys
import os

from mytool import git, prompt, util


@click.command()
@click.argument('name')
def main(name):
    btree = git.branch.branchtree()
    branches = btree.branchnames
    if name in branches:
        if not util.ask(f'"{name}" already exists, check it out?'):
            sys.exit()
        util.tryrun(f'git checkout {name}')
        return os.system('git pull')
    
    status = git.status().status
    stash = False
    if status:
        os.system('git status')
        answer = prompt.action('Uncommitted changes', 'stash => apply', 'just checkout', special_opts=True)
        if answer == 's':
            stash = True
            util.tryrun('git stash')
        elif answer == 'c':
            stash = False
    util.tryrun(f'git checkout -b {name}',
                f'git push --set-upstream origin {name}')
    if stash:
        util.tryrun('git stash apply')
        from .addcommitpush import main as addcommitpush
        addcommitpush(f'new branch: {name}')


if __name__ == '__main__':
    main()
