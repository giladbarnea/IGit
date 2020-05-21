#!/usr/bin/env python3.8
import sys
from pathlib import Path
from typing import List, Tuple
import click

from igit.status import Status
from igit.util import termcolor
from igit.util.types import PathOrStr
from igit.prompt import ask


@click.command()
@click.argument('file')
def main(file):
    gitignore = Path('.gitignore')
    if not gitignore.is_file():
        # TODO: prompt for create
        sys.exit(termcolor.red(f'{gitignore.absolute()} is not file'))
    with gitignore.open(mode='r') as f:
        data = [Path(line.strip()) for line in f.readlines()]
    file = Path(file)
    if file in data:
        data = sorted([str(p) for p in data if p != file])
        with gitignore.open(mode='w') as f:
            f.write('\n'.join(data))
        print(f'unignored {file}')
    else:
        print(f'{file} not in gitignore')


if __name__ == '__main__':
    main()
