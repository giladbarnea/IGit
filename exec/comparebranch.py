#!/usr/bin/env python3.8
import sys
import webbrowser

import click

import prompt
from branch import BranchTree
from repo import Repo
from util import termcolor


@click.command()
@click.argument('src', required=False)
@click.argument('compareto', required=False)
def main(src, compareto):
    # TODO: if either == '%version%
    print(f'src: {src}', f'compareto: {compareto}')
    btree = BranchTree()
    branches = btree.branchnames
    versionbranch = btree.version
    if not versionbranch:
        versionbranch = 'master'
    current = btree.current
    
    if not src and not compareto:  # specified nothing, compare current to version
        src = current
        compareto = versionbranch
    
    elif src:  # specified src, compare current to it
        src = current
        compareto = src
    
    if compareto not in branches:
        print(termcolor.yellow(f"didn't find {compareto} in branches"))
        compareto = btree.search(compareto)
    
    if src == compareto:
        if src == 'master':
            sys.exit(termcolor.red('Already on master.'))
        
        if src == versionbranch:  # neither is master
            if not prompt.ask(f"You're already on version branch: {versionbranch}. Compare to master?"):
                sys.exit()
            compareto = 'master'
        else:
            sys.exit(termcolor.red(f'src == compareto: {src}'))
    repo = Repo()
    if repo.host == 'bitbucket':
        url = f"https://{repo.weburl}/branches/compare/{src}%0D{compareto}#diff"
    else:
        url = f"https://{repo.weburl}/compare/{src}..{compareto}"
    webbrowser.open(url)


if __name__ == '__main__':
    main()
