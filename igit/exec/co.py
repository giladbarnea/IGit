#!/usr/bin/env python3.8

import click

from igit import git, shell
from igit import prompt
from igit.status import Status

from igit.branches import Branches
from igit.util.misc import yellowprint, brightyellowprint, redprint


@click.command()
@click.argument('branch')
def main(branch):
    status = Status()
    if status:
        if not prompt.confirm('Uncommitted changes, checkout anyway?'):
            print('aborting')
            return
    btree = Branches()
    
    if branch not in btree:
        yellowprint(f'"{branch}" not in branches, searching...')
        branch = btree.search(branch)
    if btree.current == branch:
        yellowprint(f'Already on {branch}')
        return
    if not branch:
        redprint(f"Couldn't find branch")
        return
    shell.run(f'git checkout {branch}')
    if not prompt.confirm('git pull?'):
        print('aborting')
        return
    if git.pull() == 1:
        brightyellowprint(f"git pull failed")


if __name__ == '__main__':
    main()
