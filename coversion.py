#!/usr/bin/env python3.7


from mytool import util, term, git
import sys
import os
from mytool import git


def main():
    status = git.shortstatus()
    if status:
        sys.exit(term.red('Uncommitted changes, aborting'))
    versionbranch = git.branch.version()
    if not versionbranch:
        print(term.warn("Couldn't find version branch"))
        if not util.ask('Checkout master?'):
            sys.exit()
        branch = 'master'
    else:
        branch = versionbranch
    
    currbranch = git.branch.current()
    
    if currbranch == branch:
        print(term.warn(f'Already on version branch: {branch}'))
        if not util.ask('Pull?'):
            sys.exit()
        return os.system('git pull')
    
    util.tryrun(f'git checkout {branch}')
    return os.system('git pull')


if __name__ == '__main__':
    main()
