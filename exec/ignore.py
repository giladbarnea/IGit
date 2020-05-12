#!/usr/bin/env python3.8
from typing import Union, List

import click
from util import termcolor

import sys

from status import Status
from pathlib import Path

from tipes import PathOrStr


@click.command()
@click.argument('files_to_ignore', nargs=-1)
def main(files_to_ignore: List[PathOrStr]):
    gitignore = Path('.gitignore')
    if not gitignore.is_file():
        # TODO: prompt for create
        sys.exit(termcolor.red(f'{gitignore.absolute()} is not file'))
    paths: List[Path] = []
    status = Status()
    files = status.files
    for f in files_to_ignore:
        if "*" in f:
            paths.append(f)
            continue
        try:
            if f.isdigit():
                # index
                try:
                    f = files[int(f)]
                except IndexError:
                    i = input(f'Index error with {f} (len of files: {len(files)}), try again:\t')
                    f = files[int(i)]
        except AttributeError:
            pass  # not digit
        path = Path(f)
        if not path.exists():
            print(termcolor.yellow(f'{path} does not exist, skipping'))
            continue
        paths.append(path)
    if not paths:
        sys.exit(termcolor.red('no paths'))
    
    with gitignore.open(mode='r+') as f:
        data = f.read()
        if data and data[-1] == '\n':
            prefix = ''
        else:
            prefix = '\n'
        for p in paths:
            if "*" in str(p):
                val = p
            else:
                val = f'{p}/' if p.is_dir() else p
            # TODO: check if parent of wildcard exists
            to_write = f'{prefix}{val}\n'
            if str(val) in data:
                print(termcolor.yellow(f'{val} already in gitignore, continuing'))
                continue
            f.write(to_write)
            prefix = ''
            print(termcolor.green(f'Added {val} to .gitignore'))


if __name__ == '__main__':
    main()
