#!/usr/bin/env python3.8
import webbrowser

import click

from igit import prompt
from igit.branch import BranchTree
from igit.repo import Repo


def url_subdomain(repo):
    if repo.host == 'github':
        return 'tree'
    elif repo.host == 'bitbucket':
        return 'src'
    else:
        return 'FIXME_openweb.py'


@click.command()
@click.option('--branch', '-b', required=False)
def main(branch):
    repo = Repo()
    btree = BranchTree()
    subdomain = url_subdomain(repo)
    url = f'https://{repo.weburl}/{subdomain}'
    if branch:
        # res = requests.get(f'{url}/{branch}')
        # if not res.ok:
        if branch not in btree.branchnames:
            if prompt.ask(f'"{branch}" not in branches, search?', special_opts=True):
                branch = btree.search(branch)
            else:
                branch = btree.current
    else:
        branch = btree.current
    
    url += f'/{branch}'
    return webbrowser.open(url)


if __name__ == '__main__':
    main()
