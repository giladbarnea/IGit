#!/usr/bin/env python3.7
import click

from mytool import util
from mytool import git


@click.command()
@click.argument('branch', required=False)
def main(branch):
    if branch:
        if util.ask('search?'):
            branch = git.branch.search(branch)
    else:
        branch = git.branch.current()
    util.clip_copy(branch)


if __name__ == '__main__':
    main()
