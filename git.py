#!/usr/bin/env python3.8
import os
import re
import sys

from util import termcolor, shell
import subprocess as sp


def repourl() -> str:
    lines = shell.tryrun('git remote -v').splitlines()
    if not lines:
        sys.exit(termcolor.red('"git remote -v" no output'))
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
        sys.exit(termcolor.red(f"regex: {regex} no match to lines[0]: '{line}'"))
    url = match.group()
    if isbitbucket and ':cashdash' in line:
        url = url.replace(':cashdash', '/cashdash')
    return url


def fetchall() -> int:
    return sp.call('sudo git fetch --all'.split())


def pull() -> int:
    # https://stackoverflow.com/questions/5136611/capture-stdout-from-a-script
    # from IPython.utils.capture import capture_output
    # with capture_output() as c: print('some output')
    # TODO: understand how to get colors AND output
    return sp.call('sudo git pull'.split())


def push() -> int:
    # TODO: understand how to get colors AND output
    return sp.call('sudo git push'.split())
