#!/usr/bin/env python3.7
from mytool import term, util
import click
import sys

from mytool import git
import webbrowser


@click.command()
@click.argument('src', required=False)
@click.argument('compareto', required=False)
def main(src, compareto):
    branches = git.branch.getall()
    versionbranch = git.branch.version(branches)
    if not versionbranch:
        versionbranch = 'master'
    current = git.branch.current()
    
    if not src and not compareto:  # specified nothing, compare current to version
        src = current
        compareto = versionbranch
    
    elif src:  # specified src, compare current to it
        compareto = src
        src = current
    
    if compareto not in branches:
        print(term.warn(f"didn't find {compareto} in branches"))
        compareto = git.branch.search(compareto, branches)
    
    if src == compareto:
        if src == 'master':
            sys.exit(term.red('Already on master.'))
        
        if src == versionbranch:  # neither is master
            if not util.ask(f"You're already on version branch: {versionbranch}. Compare to master?"):
                sys.exit()
            compareto = 'master'
        else:
            sys.exit(term.red(f'src == compareto: {src}'))
    webbrowser.open(f"https://{git.repourl()}/branches/compare/{src}%0D{compareto}#diff")


if __name__ == '__main__':
    main()
