#!/usr/bin/env python3.7


from mytool import util, term
import sys
import click
from mytool import git


@click.command()
@click.argument('branch')
def main(branch):
    status = git.status().status
    if status:
        if not util.ask('Uncommitted changes, continue?'):
            sys.exit('aborting')
    btree = git.branch.branchtree()
    currbranch = btree.current
    
    if currbranch == branch:
        sys.exit(term.warn(f'Already on {branch}'))
    
    branches = btree.branchnames
    if branch not in branches:
        print(term.warn(f"didn't find {branch} in branches"))
        branch = btree.search(branch)
    if not branch:
        sys.exit(term.red(f"Couldn't find branch"))
    util.tryrun(f'git checkout {branch}')
    git.pull()


if __name__ == '__main__':
    main()
