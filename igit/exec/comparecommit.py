#!/usr/bin/env python3.8


import webbrowser
import click
import sys

from igit.commit import CommitTree
from igit.repo import Repo
from more_termcolor import colors


@click.command()
@click.argument("src_hash_or_index", required=False)
@click.argument("target_hash_or_index", required=False)
def main(src_hash_or_index, target_hash_or_index):
    # TODO: support a4af4e7..0c6dd4a
    if src_hash_or_index:
        if not target_hash_or_index:
            ctree = CommitTree()
            src = ctree.current
            target = src_hash_or_index
        else:
            src = src_hash_or_index
            target = target_hash_or_index
    else:
        # TODO: compare current to one before
        sys.exit(colors.red(f'current commit is {CommitTree().current}'))
    repo = Repo()
    webbrowser.open(f"https://{repo.weburl}/branches/compare/{src}%0D{target}#diff")


if __name__ == '__main__':
    main()
