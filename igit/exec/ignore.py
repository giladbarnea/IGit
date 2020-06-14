#!/usr/bin/env python3.8
import sys
from typing import List, Tuple

import click

from igit.ignore import Gitignore
from igit.status import Status
from igit.util.clickextensions import unrequired_opt
from igit.util.path import ExPath, ExPathOrStr
from more_termcolor import colors

tabchar = '\t'


def write(paths: List[ExPath], confirm: bool, dry_run: bool):
    gitignore = Gitignore()
    if not gitignore.exists():
        # TODO: prompt for create
        sys.exit(colors.brightred(f'{gitignore.absolute()} is not file'))
    
    gitignore.write(paths, confirm=confirm, dry_run=dry_run)
    if dry_run:
        print('dry run finished')


def build_paths(exclude_parent, exclude_paths, ignore_paths) -> List[ExPath]:
    statusfiles = None
    paths: List[ExPath] = []
    for f in ignore_paths:
        # * wildcard
        if "*" in f:
            paths.append(f)
            continue
        
        # * index
        try:
            if not statusfiles:
                statusfiles = Status().files
            f = statusfiles[int(str(f))]
        except IndexError:
            i = input(f'Index error with {f} (len of files: {len(statusfiles)}), try again:\t')
            f = statusfiles[int(i)]
        except ValueError:
            pass  # not a number
        
        path = ExPath(f)
        if not path.exists():
            print(colors.yellow(f'{path} does not exist, skipping'))
            continue
        
        if path == exclude_parent:
            # path: '.config', exclude_paths: ['.config/dconf']
            for sub in filter(lambda p: p not in exclude_paths, path.iterdir()):
                paths.append(sub)
        else:
            paths.append(path)
    if not paths:
        sys.exit(colors.brightred(f'no paths in {ExPath(".").absolute()}'))
    return paths


def handle_exclude_paths(exclude_paths_str: str) -> Tuple[ExPath, List[ExPath]]:
    """Does the '.config/dconf copyq' trick"""
    if not exclude_paths_str:
        return None, None
    if '/' in exclude_paths_str:
        exclude_parent, _, exclude_paths = exclude_paths_str.rpartition('/')
        exclude_parent = ExPath(exclude_parent)
        exclude_paths = [exclude_parent / ExPath(ex) for ex in exclude_paths.split(' ')]
    else:
        raise NotImplementedError(f'only currently handled format is `.ipython/profile_default/startup ipython_config.py`')
    return exclude_parent, exclude_paths


def ignore(confirm: bool, dry_run: bool, ignore_paths, exclude_paths_str: str = None):
    exclude_parent, exclude_paths = handle_exclude_paths(exclude_paths_str)
    if exclude_paths:
        if not ignore_paths:
            ignore_paths = [exclude_parent]
    
    else:
        if not ignore_paths:
            raise ValueError("Either ignore_paths, exclude_paths or both must be passed")
        # exclude_parent = None
    paths = build_paths(exclude_parent, exclude_paths, ignore_paths)
    write(paths, confirm, dry_run)


@click.command()
@click.argument('ignore_paths', nargs=-1)
@unrequired_opt('-e', '--exclude', 'exclude_paths_tuple', multiple=True, type=str,
                help=f"""will NOT be added to gitignore. must be subpaths of a dir passed in IGNORE_PATHS.\n
                    Examples:\n
                    {colors.italic('-e .config/dconf copyq')}\n
                    {colors.italic('-e .ipython/profile_default/startup ipython_config.py')}\n
                    {colors.italic('-e .oh-my-zsh/plugins/colored-man-pages/colored-man-pages.plugin.zsh -e .oh-my-zsh/plugins/globalias/globalias.plugin.zsh')}\n
                    """)
@unrequired_opt('-c', '--confirm', help='confirm before each write. flag.', is_flag=True)
@unrequired_opt('-n', '--dry-run', help='dont actually write to file. flag.', is_flag=True)
def main(ignore_paths: List[ExPathOrStr], exclude_paths_tuple: Tuple[str, ...], confirm, dry_run):
    if exclude_paths_tuple:
        for exclude_paths_str in exclude_paths_tuple:
            ignore(confirm, dry_run, ignore_paths, exclude_paths_str)
    else:
        ignore(confirm, dry_run, ignore_paths)


if __name__ == '__main__':
    main()
