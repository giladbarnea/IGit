#!/usr/bin/env python3.7


from mytool import util, term
import sys
import click
from mytool import git


@click.command()
@click.argument('branch')
def main(branch):
    status = git.shortstatus()
    if status:
        if not util.ask('Uncommitted changes, continue?'):
            sys.exit('aborting')
    currbranch = git.branch.current()
    
    if currbranch == branch:
        sys.exit(term.warn(f'Already on {branch}'))
    
    branches = git.branch.getall()
    if branch not in branches:
        print(term.warn(f"didn't find {branch} in branches"))
        branch = git.branch.search(branch, branches)
    util.tryrun(f'git checkout {branch}', f'git pull')


if __name__ == '__main__':
    main()
