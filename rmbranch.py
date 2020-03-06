#!/usr/bin/env python3.7
from mytool import util, term
import click
import sys

from mytool import git


@click.command()
@click.argument('name')
def main(name):
    branches = git.branch.getall()
    if name not in branches:
        print(term.warn(f"didn't find {name} in branches"))
        name = git.branch.search(name, branches)
    if name == git.branch.current():
        # TODO: gco - then continue
        sys.exit(term.red(f'"{name}" is current branch'))
    if name == git.branch.version(branches):
        if not util.ask(f'{name} is version branch, continue?'):
            sys.exit()
    util.tryrun(f'git branch -D {name}',
                f'git push origin --delete {name}')


if __name__ == '__main__':
    main()
