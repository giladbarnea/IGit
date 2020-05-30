#!/usr/bin/env python3.8
import sys
import webbrowser

import click

from igit import prompt
from igit.branch import BranchTree
from igit.repo import Repo
from igit.util import termcolor

btree = BranchTree()


def compare(a, b):
    print(termcolor.lightgrey(f'compare("{a}", "{b}")'))
    if a == b:
        sys.exit(termcolor.red(f'trying to compare a branch to itself: {a}'))
    if a not in btree.branches:
        print(termcolor.yellow(f'"{a}" not in branches, searching...'))
        return compare(btree.search(a), b)
    if b not in btree.branches:
        print(termcolor.yellow(f'"{b}" not in branches, searching...'))
        return compare(a, btree.search(b))
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
    print(termcolor.lightgrey(f'main(a: {a}, b: {b})'))
    if a and b:
        print(termcolor.lightgrey(f'comparing a to b'))
        return compare(a, b)
    if a:
        print(termcolor.lightgrey(f'comparing btree.current to a'))
        return compare(btree.current, a)
    
    print(termcolor.lightgrey(f'comparing btree.current to master'))
    return compare(btree.current, 'master')


if __name__ == '__main__':
    main()
