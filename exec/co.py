#!/usr/bin/env python3.8
import sys

import click

import git
import prompt
from status import Status
from util import shell, termcolor

from branch import BranchTree


@click.command()
@click.argument('branch')
def main(branch):
    status = Status()
    if status:
        if not prompt.ask('Uncommitted changes, continue?'):
            sys.exit('aborting')
    btree = BranchTree()
    currbranch = btree.current
    
    if currbranch == branch:
        sys.exit(termcolor.yellow(f'Already on {branch}'))
    
    branches = btree.branchnames
    if branch not in branches:
        print(termcolor.yellow(f"didn't find {branch} in branches"))
        branch = btree.search(branch)
    if not branch:
        sys.exit(termcolor.red(f"Couldn't find branch"))
    shell.tryrun(f'git checkout {branch}')
    if git.pull() == 1:
        print(termcolor.yellow(f"git pull failed"))


if __name__ == '__main__':
    main()
