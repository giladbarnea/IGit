#!/usr/bin/env python3.7
from mytool import term, util
import click
import sys

from mytool import git
import webbrowser


def is_file(val):
    pass


def is_branch(val):
    pass


unrequired_opts = dict(default=None, required=False, show_default=True)


@click.command()
@click.option('--branch', '-b', **unrequired_opts)
@click.option('--files', '-f', **unrequired_opts)
@click.option('--exclude', '-e', **unrequired_opts, default='.log')
def main(branch, files, exclude):
    # git diff origin/master -- . :(exclude)*.csv :(exclude)*.ipynb :(exclude)*.sql :!report_validators/*
    # everything is space separated, like grepf.py
    # TODO: in exclude, :!report_validators/* if dir else :!*.ipynb
    #  same for files
    #  option to view in web like comparebranch
    btree = git.branch.branchtree()
    branches = btree.branchnames
    versionbranch = btree.version
    if not versionbranch:
        versionbranch = 'master'
    current = btree.current
    
    if not src and not compareto:  # specified nothing, compare current to version
        src = current
        compareto = versionbranch
    
    elif src:  # specified src, compare current to it
        compareto = src
        src = current
    
    if compareto not in branches:
        print(term.warn(f"didn't find {compareto} in branches"))
        compareto = btree.search(compareto)
    
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
