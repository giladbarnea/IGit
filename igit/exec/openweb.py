#!/usr/bin/env python3.8
import webbrowser

import click

from igit import prompt
from igit.branches import Branches
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
    btree = Branches()
    subdomain = url_subdomain(repo)
    url = f'https://{repo.weburl}/{subdomain}'
    if branch:
        # res = requests.get(f'{url}/{branch}')
        # if not res.ok:
        if branch not in btree:
            if prompt.confirm(f'"{branch}" not in branches, search?', flowopts=True):
                branch = btree.search(branch)
            else:
                branch = btree.current
    else:
        branch = btree.current
    
    url += f'/{branch}'
    return webbrowser.open(url)


if __name__ == '__main__':
    main()
