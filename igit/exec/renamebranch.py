#!/usr/bin/env python3.8
import os
import sys

import click

from igit.status import Status
from more_termcolor import colors
from igit import shell

from igit.branches import Branches


@click.command()
@click.argument('oldname')
@click.argument('newname')
def main(oldname, newname):
    status = Status()
    if status:
        sys.exit(colors.red('Uncommitted changes, aborting'))
    btree = Branches()
    if newname in btree:
        sys.exit(colors.red(f'"{newname}" already exists'))
    if oldname not in btree:
        os.system('git branch -l')
        sys.exit(colors.red(f'"{oldname}" doesnt exist'))
    
    shell.run(f'git branch -m {newname}',
                 f'git push origin :{oldname} {newname}',
                 f'git push origin -u {newname}')


if __name__ == '__main__':
    main()
