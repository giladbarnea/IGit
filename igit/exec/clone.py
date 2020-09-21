#!/usr/bin/env python3.8
from typing import Literal

import click
from igit import shell
from igit.util.clickextensions import unrequired_opt

# from igit.user import User

Host = Literal['gh', 'github']


def build_url(repo: str, host: Host, owner):
    if host in ('gh', 'github'):
        host = 'github.com'
    else:
        raise NotImplementedError(f'host = "{host}"')
    
    if repo.startswith('https'):
        ret = repo
    
    elif repo.startswith('www') or repo.startswith(host):
        ret = f'https://{repo}'
    else:
        if repo.count('/') > 0:
            if repo.count('/') > 1:
                raise NotImplementedError(f'repo has more than 1 forslash. only knows 1 forslash means owner. repo = "{repo}"')
            owner, _, repo = repo.partition('/')
        if not owner:
            raise ValueError(f"expected some owner, got: {repr(owner)}")
        ret = f'https://{host}/{owner}/{repo}'
    
    if not ret.endswith('.git'):
        ret += '.git'
    return ret


@click.command()
@click.argument('repo')
@click.argument('directory', required=False, default=None)
@unrequired_opt('-h', '--host', default='gh', type=Host)
@unrequired_opt('-o', '--owner', default='giladbarnea')
@unrequired_opt('-b', '--branch', default='master')
@unrequired_opt('-g', '--separate-git-dir')
def main(repo, directory, host: Host, owner, branch, separate_git_dir):
    """REPO can also be:
      
        - 'rii-mango/NIFTI-Reader-JS'
        
        - 'github.com/rii-mango/NIFTI-Reader-JS'
        
        - 'www.github.com/rii-mango/NIFTI-Reader-JS'
        
        - 'https://github.com/rii-mango/NIFTI-Reader-JS'
        
        - 'https://www.github.com/rii-mango/NIFTI-Reader-JS'
    
    """
    from igit_debug.loggr import Loggr
    
    logger = Loggr()
    logger.debug(f'repo: {repo}, ', f'directory: {directory}, ', f'host: {host}, ', f'owner: {owner}, ', f'branch: {branch}, ', f'separate_git_dir: {separate_git_dir}')
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
