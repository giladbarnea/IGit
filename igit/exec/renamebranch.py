#!/usr/bin/env python3.8
import os
import sys

import click

from igit.status import Status
from igit.util import termcolor
from igit.util import shell

from igit.branch import BranchTree


@click.command()
@click.argument('oldname')
@click.argument('newname')
def main(oldname, newname):
    status = Status()
    if status:
        sys.exit(termcolor.red('Uncommitted changes, aborting'))
    btree = BranchTree()
    branches = btree.branchnames
    if newname in branches:
        sys.exit(termcolor.red(f'"{newname}" already exists'))
    if oldname not in branches:
        os.system('git branch -l')
        sys.exit(termcolor.red(f'"{oldname}" doesnt exist'))
    
    shell.tryrun(f'git branch -m {newname}',
                 f'git push origin :{oldname} {newname}',
                 f'git push origin -u {newname}')


if __name__ == '__main__':
    main()
