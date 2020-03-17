#!/usr/bin/env python3.7
from mytool import git, util
import webbrowser
import click
import requests


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
    repo = git.repo()
    btree = git.branch.branchtree()
    subdomain = url_subdomain(repo)
    url = f'https://{repo.weburl}/{subdomain}'
    if branch:
        # res = requests.get(f'{url}/{branch}')
        # if not res.ok:
        if branch not in btree.branchnames:
            if util.ask(f'"{url}/{branch}" failed, search?', 'yes', 'no (open with current)', 'quit'):
                branch = btree.search(branch)
            else:
                branch = btree.current
    else:
        branch = btree.current
    
    url += f'/{branch}'
    return webbrowser.open(url)


if __name__ == '__main__':
    main()
