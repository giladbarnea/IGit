#!/usr/bin/env python3.7
import sys
import os
from mytool import term, util
import re


def repourl() -> str:
    lines = util.tryrun('git remote -v').splitlines()
    if not lines:
        sys.exit(term.red('"git remote -v" no output'))
    line = lines[0]
    isbitbucket = 'bitbucket' in line
    if isbitbucket:
        regex = r'bitbucket.org.*(?=\.git)\b'
    elif 'github' in line:
        regex = r'github.com.*(?=\.git)\b'
    else:
        raise ValueError(f"repourl(): not github nor bitbucket. {line}")
    match = re.search(regex, line)
    if not match:
        # TODO: print remotes then input by index
        sys.exit(term.red(f"regex: {regex} no match to lines[0]: '{line}'"))
    url = match.group()
    if isbitbucket and ':cashdash' in line:
        url = url.replace(':cashdash', '/cashdash')
    return url


def repo() -> str:
    return repourl().split('/')[-1]


def fetchall() -> str:
    return util.tryrun('git fetch --all')


def pull():
    # TODO: understand how to get colors AND output (sp.run?)
    os.system('git pull')
