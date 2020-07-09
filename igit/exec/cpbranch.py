#!/usr/bin/env python3.8
import click

from igit.branches import Branches
from igit import prompt
from igit.util.misc import clip_copy


@click.command()
@click.argument('branch', required=False)
def main(branch):
    btree = Branches()
    if branch:
        if prompt.confirm('search?'):
            branch = btree.search(branch)
    else:
        branch = btree.current
    clip_copy(branch)


if __name__ == '__main__':
    main()
