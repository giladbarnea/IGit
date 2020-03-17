#!/usr/bin/env python3.7
from mytool import term, util
import sys
import os
import click

from mytool import git


@click.command()
@click.argument('oldname')
@click.argument('newname')
def main(oldname, newname):
    status = git.status().status
    if status:
        sys.exit(term.red('Uncommitted changes, aborting'))
    btree = git.branch.branchtree()
    branches = btree.branchnames
    if newname in branches:
        sys.exit(term.red(f'"{newname}" already exists'))
    if oldname not in branches:
        os.system('git branch -l')
        sys.exit(term.red(f'"{oldname}" doesnt exist'))
    
    util.tryrun(f'git branch -m {newname}',
                f'git push origin :{oldname} {newname}',
                f'git push origin -u {newname}')


if __name__ == '__main__':
    main()
