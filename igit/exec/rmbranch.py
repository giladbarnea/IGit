#!/usr/bin/env python3.8
import sys

import click

from igit import prompt
from igit.util import shell, termcolor

from igit.branch import BranchTree


@click.command()
@click.argument('name')
def main(name):
    btree = BranchTree()
    branches = btree.branchnames
    if name not in branches:
        print(termcolor.yellow(f"didn't find {name} in branches"))
        name = btree.search(name)
    if name == btree.current:
        # TODO: gco - then continue
        sys.exit(termcolor.red(f'"{name}" is current branch'))
    if name == btree.version:
        if not prompt.ask(f'{name} is version branch, continue?'):
            sys.exit()
    shell.tryrun(f'git branch -D {name}',
                 f'git push origin --delete {name}')


if __name__ == '__main__':
    main()
