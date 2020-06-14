#!/usr/bin/env python3.8
import click
from igit.util import shell
from igit.util.clickextensions import unrequired_opt
from igit.user import User


def build_url(repo, host, owner):
    if host in ('gh', 'github'):
        host = 'github.com'
    else:
        raise NotImplementedError(f'host = "{host}"')
    
    if repo.startswith('https'):
        ret = repo
    
    elif repo.startswith('www') or repo.startswith(host):
        ret = f'https://{repo}'
    else:
        if not owner:
            raise ValueError(f"expected some owner, got: {repr(owner)}")
        ret = f'https://{host}/{owner}/{repo}'
    
    if not ret.endswith('.git'):
        ret += '.git'
    return ret


@click.command()
@click.argument('repo')
@click.argument('directory', required=False, default=None)
@unrequired_opt('-h', '--host', default='gh')
@unrequired_opt('-o', '--owner', default='giladbarnea')
@unrequired_opt('-b', '--branch', default='master')
@unrequired_opt('-g', '--separate-git-dir')
def main(repo, directory, host, owner, branch, separate_git_dir):
    cmd = 'git clone '
    if branch != 'master':
        cmd += f'--branch={branch} '
    if separate_git_dir:
        cmd += f'--separate-git-dir={separate_git_dir} '
    
    cmd += build_url(repo, host, owner)
    if directory:
        cmd += f' {directory}'
    shell.run(cmd)


if __name__ == '__main__':
    main()
