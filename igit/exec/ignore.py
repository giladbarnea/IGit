#!/usr/bin/env python3.8
import sys
from typing import List, Tuple

import click

from igit import prompt
from igit.ignore import Gitignore
from igit.status import Status
from igit.util.clickextensions import unrequired_opt
from igit.util.misc import darkprint
from igit.expath import ExPath, ExPathOrStr
from more_termcolor import colors
from more_termcolor.colors import italic as ita, dark
from igit_debug.loggr import Loggr

logger = Loggr(__name__)
tabchar = '\t'


def write(paths: List[ExPath], confirm: bool, dry_run: bool, backup: bool):
    gitignore = Gitignore()
    gitignore.write(paths, confirm=confirm, dry_run=dry_run, backup=backup)
    if dry_run:
        print('dry run finished')


def build_paths(exclude_parent, exclude_paths, ignore_paths) -> List[ExPath]:
    logger.debug(f'exclude_parent:', exclude_parent, 'exclude_paths:', exclude_paths, 'ignore_paths:', ignore_paths)
    statusfiles = None
    paths: List[ExPath] = []
    skip_non_existent = False
    ignore_non_existent = False
    for f in ignore_paths:
        # * wildcard
        if "*" in f:
            paths.append(f)  # TODO: now that ExPath supports glob, ...
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
            if skip_non_existent:
                continue
            if not ignore_non_existent:
                key, choice = prompt.action(f'{path} does not exist', 'skip', 'ignore anyway', sA='skip all', iA='ignore all')
                if key == 'skip':
                    continue
                if key == 'sA':
                    skip_non_existent = True
                elif key == 'iA':
                    ignore_non_existent = True
                
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


def ignore(confirm: bool, dry_run: bool, backup: bool, ignore_paths, exclude_paths_str: str = None):
    exclude_parent, exclude_paths = handle_exclude_paths(exclude_paths_str)
    if exclude_paths:
        if not ignore_paths:
            ignore_paths = [exclude_parent]
    
    else:
        if not ignore_paths:
            raise ValueError("Either ignore_paths, exclude_paths or both must be passed")
        # exclude_parent = None
    paths = build_paths(exclude_parent, exclude_paths, ignore_paths)
    write(paths, confirm, dry_run, backup)


@click.command()
@click.argument('ignore_paths', nargs=-1)
@unrequired_opt('-e', '--exclude', 'exclude_paths_tuple', multiple=True, type=str,
                help=f"""-e <ignore_all_items_in_this_path>/<except_this_item> [<and_this_item>, ...]\n
                    All items under left of '/' will be ignored one by one, \n
                    except all space-separated right of '/'.\n
                    Left of '/' must be subpath of a dir in IGNORE_PATHS.\n
                    Examples:\n
                    {ita('-e .config/dconf copyq')} {dark("all .config/* items are ignored except 'dconf' and 'copyq' dirs")}\n
                    {ita('-e .ipython/profile_default/startup ipython_config.py')} {dark("all .ipython/profile_default/* items except 'startup' dir and 'ipython_config.py' file")}\n
                    {ita('-e .oh-my-zsh/plugins/colored-man-pages/colored-man-pages.plugin.zsh -e .oh-my-zsh/plugins/globalias/globalias.plugin.zsh')}\n
                    """)
@unrequired_opt('-c', '--confirm', help='confirm before each write. flag.', is_flag=True)
@unrequired_opt('-n', '--dry-run', help='dont actually write to file. flag.', is_flag=True)
@unrequired_opt('-b', '--backup', help='create a .gitignore.backup before making changes. flag.', is_flag=True, default=True)
def main(ignore_paths: List[ExPathOrStr], exclude_paths_tuple: Tuple[str, ...], confirm:bool=False, dry_run:bool=False, backup:bool=True):
    # TODO: support i.e. "e/h/package" for "efficient-frontier/home-task/package-lock.json"
    darkprint(f'ignore.py main() | ignore_paths: {ignore_paths}, exclude_paths_tuple: {exclude_paths_tuple}, confirm: {confirm}, dry_run: {dry_run}, backup: {backup}')
    if exclude_paths_tuple:
        for exclude_paths_str in exclude_paths_tuple:
            ignore(confirm, dry_run, backup, ignore_paths, exclude_paths_str)
    else:
        ignore(confirm, dry_run, backup, ignore_paths)


if __name__ == '__main__':
    main()
