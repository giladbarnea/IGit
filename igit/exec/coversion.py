#!/usr/bin/env python3.8
import sys

from igit import git
from igit import prompt
from igit.branch import BranchTree
from igit.status import Status
from igit.util import shell
from more_termcolor import colors


def main():
    status = Status()
    if status:
        sys.exit(colors.red('Uncommitted changes, aborting'))
    btree = BranchTree()
    versionbranch = btree.version
    if not versionbranch:
        print(colors.yellow("Couldn't find version branch"))
        if not prompt.confirm('Checkout master?'):
            sys.exit()
        branch = 'master'
    else:
        branch = versionbranch
    
    currbranch = btree.current
    
    if currbranch == branch:
        print(colors.yellow(f'Already on version branch: {branch}'))
        if not prompt.confirm('Pull?'):
            sys.exit()
        if git.pull() == 1:
            print(colors.yellow(f"git pull failed"))
    
    shell.run(f'git checkout {branch}')
    if git.pull() == 1:
        print(colors.yellow(f"git pull failed"))


if __name__ == '__main__':
    main()
