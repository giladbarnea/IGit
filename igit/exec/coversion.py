#!/usr/bin/env python3.8
import sys

from igit import git
from igit import prompt
from igit.branch import BranchTree
from igit.status import Status
from igit.util import shell, termcolor


def main():
    status = Status()
    if status:
        sys.exit(termcolor.red('Uncommitted changes, aborting'))
    btree = BranchTree()
    versionbranch = btree.version
    if not versionbranch:
        print(termcolor.yellow("Couldn't find version branch"))
        if not prompt.ask('Checkout master?'):
            sys.exit()
        branch = 'master'
    else:
        branch = versionbranch
    
    currbranch = btree.current
    
    if currbranch == branch:
        print(termcolor.yellow(f'Already on version branch: {branch}'))
        if not prompt.ask('Pull?'):
            sys.exit()
        if git.pull() == 1:
            print(termcolor.yellow(f"git pull failed"))
    
    shell.tryrun(f'git checkout {branch}')
    if git.pull() == 1:
        print(termcolor.yellow(f"git pull failed"))


if __name__ == '__main__':
    main()
