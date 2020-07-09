#!/usr/bin/env python3.8
import sys
import webbrowser

import click
from more_termcolor import colors

from igit.branches import Branches
from igit.repo import Repo
from igit.util.misc import yellowprint, darkprint

btree = Branches()


def compare(a, b):
    darkprint(f'compare({repr(a)}, {repr(b)})')
    if a == b:
        sys.exit(colors.red(f'trying to compare a branch to itself: {a}'))
    if a not in btree:
        yellowprint(f'"{a}" not in branches, searching...')
        a = btree.search(a)
    if b not in btree:
        yellowprint(f'"{b}" not in branches, searching...')
        b = btree.search(b)
    
    repo = Repo()
    if repo.host == 'bitbucket':
        url = f"https://{repo.weburl}/branches/compare/{a}%0D{b}#diff"
    else:
        url = f"https://{repo.weburl}/compare/{a}..{b}"
    webbrowser.open(url)


@click.command()
@click.argument('a', required=False)
@click.argument('b', required=False)
def main(a, b):
    darkprint(f'main(a: {a}, b: {b})')
    if a and b:
        darkprint(f'comparing a to b')
        return compare(a, b)
    if a:
        darkprint(f'comparing btree.current to a')
        return compare(btree.current, a)
    
    # not a and not b
    darkprint(f'comparing btree.current to master')
    return compare(btree.current, 'master')


if __name__ == '__main__':
    main()
