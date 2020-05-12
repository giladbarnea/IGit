#!/usr/bin/env python3.8
import os
from typing import Tuple

import click

from igit.status import Status


def is_file(val):
    pass


def is_branch(val):
    pass


@click.command()
@click.argument('items', nargs=-1, required=False)
@click.option('--exclude', '-e', default=None, required=False, show_default=True)
def main(items: Tuple[str], exclude):
    # git diff origin/master -- . :(exclude)*.csv :(exclude)*.ipynb :(exclude)*.sql :!report_validators/*
    # everything is space separated, like grepf.py
    # TODO: in exclude, :!report_validators/* if dir else :!*.ipynb
    #  same for files
    #  option to view in web like comparebranch
    # -b: --ignore-space-change, -w: --ignore-all-space. allow-indentation-change?
    cmd = 'git diff --ignore-cr-at-eol --ignore-space-at-eol -b -w --ignore-blank-lines'
    print(f'items: {items}')
    if not items:
        return os.system(cmd)
    first, *rest = items
    if not rest:
        status = Status()
        files = status[first]
        joined = " ".join(map(str, files))
        print(f'files: {files}', 'joined: ', joined)
        return os.system(f'{cmd} {joined}')


if __name__ == '__main__':
    main()
