#!/usr/bin/env python3.7
from pathlib import Path
from typing import List, Tuple, Dict
import sys
import os
from mytool import term, util
import re


def file_status_map() -> Dict[Path, str]:
    def _clean_shortstatus(_x) -> Tuple[Path, str]:
        _file, _status = _x[3:].replace('"', ''), _x[:3].strip()
        if 'R' in _status:
            if '->' not in _file:
                raise ValueError(f"'R' in status but '->' not in file. file: {_file}, status: {_status}", locals())
            _, _, _file = _file.partition(' -> ')  # return only existing
        else:
            if '->' in _file:
                raise ValueError(f"'R' not in status but '->' in file. file: {_file}, status: {_status}", locals())
        return Path(_file), _status
    
    status = shortstatus()
    return dict([_clean_shortstatus(s) for s in status])


def statusfiles() -> List[Path]:
    return list(file_status_map().keys())


def shortstatus() -> List[str]:
    return util.tryrun('git status -s', printout=False, printcmd=False).splitlines()


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
