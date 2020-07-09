#!/usr/bin/env python3.8
import sys

import click

from igit import prompt
from igit.util import shell

from igit.branches import Branches
from more_termcolor import colors


@click.command()
@click.argument('name')
def main(name):
    btree = Branches()
    if name not in btree:
        print(colors.yellow(f"didn't find {name} in branches"))
        name = btree.search(name)
    if name == btree.current:
        # TODO: gco - then continue
        sys.exit(colors.red(f'"{name}" is current branch'))
    if name == btree.version:
        if not prompt.confirm(f'{name} is version branch, continue?'):
            sys.exit()
    shell.run(f'git branch -D {name}',
              f'git push origin --delete {name}')


if __name__ == '__main__':
    main()
