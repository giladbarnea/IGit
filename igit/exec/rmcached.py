#!/usr/bin/env python3.8
import os
import sys

from igit import prompt, git
from igit.util import termcolor, shell
from igit.util.misc import unquote


def main():
    args = sys.argv[1:]
    cwd = os.getcwd()
    print('bash args: ', args, 'bool(args):', bool(args))
    if not args:
        sys.exit(termcolor.red('no args! exiting'))
    
    cmds = []
    basenames = []
    for a in args:
        a = unquote(a)
        abspath = os.path.join(cwd, a)
        if not os.path.exists(abspath):
            print(f"{termcolor.yellow(abspath)} does not exist, skipping")
            continue
        
        # exists
        if os.path.isfile(abspath):
            cmds.append(f'git rm --cached {a}')
        elif os.path.isdir(abspath):
            cmds.append(f'git rm -r --cached {a}')
        else:
            print(f'{termcolor.yellow(abspath)} is not file nor dir, skipping (weird)')
            continue
        
        # exists and is file or dir
        basenames.append(os.path.basename(a))
    
    if not cmds:
        sys.exit(termcolor.red('no files to rm, exiting'))
    
    for c in cmds:
        shell.tryrun(c, abortonfail=False)
    
    commitmsg = f'Removed from cache: ' + ', '.join(basenames)
    shell.tryrun(f'git commit -a -m "{commitmsg}"')
    if prompt.ask('push?'):
        git.push()


if __name__ == '__main__':
    main()
