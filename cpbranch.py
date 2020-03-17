#!/usr/bin/env python3.7
import click

from mytool import util
from mytool import git


@click.command()
@click.argument('branch', required=False)
def main(branch):
    btree = git.branch.branchtree()
    if branch:
        if util.ask('search?'):
            branch = btree.search(branch)
    else:
        branch = btree.current
    util.clip_copy(branch)


if __name__ == '__main__':
    main()
