#!/usr/bin/env python3.8
import sys
from pathlib import Path
from typing import List, Tuple
import click

from igit.status import Status
from igit.util import termcolor
from igit.util.misc import unreq_opts
from igit.util.types import PathOrStr
from igit.prompt import ask


def write(paths, confirm, dry_run):
    gitignore = Path('.gitignore')
    if not gitignore.is_file():
        # TODO: prompt for create
        sys.exit(termcolor.red(f'{gitignore.absolute()} is not file'))
    with gitignore.open(mode='r+') as f:
        # TODO: sort alphabetically
        data = f.read()
        if data and data[-1] == '\n':
            prefix = ''
        else:
            prefix = '\n'
        for p in paths:
            if "*" in str(p):
                val = p
            else:
                val = f'{p}/' if p.is_dir() else p
            # TODO: check if parent of wildcard exists
            to_write = f'{prefix}{val}\n'
            if str(val) in data:
                print(termcolor.yellow(f'{val} already in gitignore, continuing'))
                continue
            if confirm and not ask(f'ignore {to_write}?'):
                continue
            if not dry_run:
                f.write(to_write)
            prefix = ''
            print(termcolor.green(f'Added {val} to .gitignore'))
    if dry_run:
        print('dry run finished')


def build_paths(exclude_parent, exclude_paths, ignore_paths):
    statusfiles = None
    paths: List[Path] = []
    for f in ignore_paths:
        # * wildcard
        if "*" in str(f):
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
        
        path = Path(f)
        if not path.exists():
            print(termcolor.yellow(f'{path} does not exist, skipping'))
            continue
        
        if path == exclude_parent:
            # path: '.config', exclude_paths: ['.config/dconf']
            for sub in filter(lambda p: p not in exclude_paths, path.iterdir()):
                paths.append(sub)
        else:
            paths.append(path)
    if not paths:
        sys.exit(termcolor.red(f'no paths in {Path(".").absolute()}'))
    return paths


def handle_exclude_paths(exclude_paths_str: str) -> Tuple[Path, List[Path]]:
    if not exclude_paths_str:
        return None, None
    if '/' in exclude_paths_str:
        exclude_parent, _, exclude_paths = exclude_paths_str.rpartition('/')
        exclude_parent = Path(exclude_parent)
        exclude_paths = [exclude_parent / Path(ex) for ex in exclude_paths.split(' ')]
    else:
        raise NotImplementedError(f'only currently handled format is `.ipython/profile_default/startup ipython_config.py`')
    return exclude_parent, exclude_paths


def ignore(confirm, dry_run, ignore_paths, exclude_paths_str: str = None):
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
@click.option('-e', '--exclude', 'exclude_paths_tuple', multiple=True, **unreq_opts(''),
              help="""space separated paths to NOT add to gitignore. must be subpaths of a dir passed in IGNORE_PATHS.\n
                    examples:\n
                    -e .config/dconf copyq\n
                    -e .ipython/profile_default/startup ipython_config.py\n
                    -e .oh-my-zsh/plugins/colored-man-pages/colored-man-pages.plugin.zsh -e .oh-my-zsh/plugins/globalias/globalias.plugin.zsh\n
                    """)
@click.option('-c', '--confirm', help='confirm before each write. flag.', **unreq_opts(False), is_flag=True)
@click.option('-n', '--dry-run', help='dont actually write to file. flag.', **unreq_opts(False), is_flag=True)
def main(ignore_paths: List[PathOrStr], exclude_paths_tuple: Tuple[str, ...], confirm, dry_run):
    if exclude_paths_tuple:
        for exclude_paths_str in exclude_paths_tuple:
            ignore(confirm, dry_run, ignore_paths, exclude_paths_str)
    else:
        ignore(confirm, dry_run, ignore_paths)


if __name__ == '__main__':
    main()
