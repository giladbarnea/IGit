#!/usr/bin/env python3.7
from mytool import term, util
import sys
import os
import re

args = sys.argv[1:]
cwd = os.getcwd()
print('bash args: ', args, 'bool(args):', bool(args))
if not args:
    sys.exit('no args! exiting')

cmds = []
basenames = []
for a in args:
    a = util.removequotes(a)
    abspath = os.path.join(cwd, a)
    if not os.path.exists(abspath):
        print(f"{term.warn(abspath)} does not exist, skipping")
        continue
    
    # exists
    if os.path.isfile(abspath):
        cmds.append(f'git rm --cached {a}')
    elif os.path.isdir(abspath):
        cmds.append(f'git rm -r --cached {a}')
    else:
        print(f'{term.warn(abspath)} is not file nor dir, skipping (weird)')
        continue
    
    # exists and is file or dir
    
    basenames.append(os.path.basename(a))

if not cmds:
    sys.exit(term.red('no files to rm, exiting'))

for c in cmds:
    util.tryrun(c, abortonfail=False)

commitmsg = f'Removed from cache: ' + ', '.join(basenames)
util.tryrun(f'git commit -a -m "{commitmsg}"', 'git push')
