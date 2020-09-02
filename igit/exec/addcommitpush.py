#!/usr/bin/env python3.8
import os
from typing import Dict

import click
from more_termcolor import colors

from igit import git, prompt, shell
from igit.exec.ignore import main as ignore
from igit.status import Status
from igit.util import misc
from igit.util.clickextensions import unrequired_opt

# called by _split_file()
from igit.expath import ExPath


def _handle_splits(promptstr, main_file: ExPath, cwd, split_prefix, dry_run: bool):
    """Handles the situation having the main file and existing splits (just created or pre-existed).
    Verifies split integrity and prompts whether to ignore or trash main file"""
    if prompt.confirm("temporarily join splits and verify integrity against main file?"):
        os.system(f'cat "{split_prefix}"* > /tmp/joined')
        if shell.run(f'diff /tmp/joined "{main_file}"'):
            prompt.generic(f"splits of '{main_file}' aren't good", flowopts=('quit', 'debug'))
        misc.greenprint('splits are good')
        shell.run('rm /tmp/joined')
    
    key, answer = prompt.action(promptstr, 'ignore main file',
                                'move main file to trash://',
                                flowopts='quit')
    if key == 'i':
        ignore(main_file.relative_to(cwd), dry_run=dry_run)
    else:
        # key == 'm'
        if dry_run:
            misc.whiteprint('dry run, not trashing file')
        else:
            shell.run(f'gio trash "{main_file}"')


# called by handle_large_files()
def _split_file(abspath: ExPath, cwd, dry_run: bool):
    # file.zip → file_zip_
    # split_prefix = abspath.with_name(abspath.stem + f'_{abspath.suffix[1:]}_').with_suffix('')
    # splits = list(abspath.parent.glob(f'"{split_prefix.stem}"*'))
    # if splits:
    try:
        splits = abspath.split()
    except FileExistsError as e:
        misc.whiteprint('found pre-existing splits')
        splits = abspath.getsplits()
        biggest_split = max(map(lambda split: split.lstat().st_size / 1000000, splits))
        _handle_splits(f'found {len(splits)} pre-existing splits, biggest is {biggest_split}MB.',
                       abspath,
                       cwd,
                       split_prefix,
                       dry_run)
        return
    
    misc.whiteprint('no pre-existing splits found. splitting...')
    if dry_run:
        misc.whiteprint('dry run, not actually splitting. continuing to next file')
        return
    shell.run(f'split -d --bytes 49000KB "{abspath}" "{split_prefix}"')
    
    splits = list(abspath.parent.glob(f'"{split_prefix.stem}"*'))
    _handle_splits(f'created {len(splits)} splits.', abspath, cwd, split_prefix, dry_run)


# called by get_large_files_from_status() and recursively
def _get_large_files_in_dir(path: ExPath) -> Dict[ExPath, float]:
    large_subfiles = {}
    for p in path.iterdir():
        if not p.exists():
            misc.yellowprint(f'does not exist: {repr(p)}')
            continue
        if p.is_file():
            mb = p.lstat().st_size / 1000000
            if mb >= 50:
                large_subfiles[p] = mb
        else:
            large_subfiles.update(_get_large_files_in_dir(p))
    return large_subfiles


def handle_large_files(cwd, largefiles: Dict[ExPath, float], dry_run: bool):
    misc.whiteprint(f'{len(largefiles)} large files sized >= 50MB found:')
    for abspath, mbsize in largefiles.items():
        stats = f'{abspath.relative_to(cwd)} ({mbsize}MB)'
        misc.whiteprint(stats)
    key, answer = prompt.action('What to do?',
                                'ignore all',
                                'split all (checks for pre-existing before splitting)',
                                'choose individually whether to ignore or split',
                                flowopts=True)
    if key == 'i':
        ignore([p.relative_to(cwd) for p in largefiles], dry_run=dry_run)
    
    elif key == 's':  # split all
        for abspath, mbsize in largefiles.items():
            _split_file(abspath, cwd, dry_run)
    
    elif key == 'c':  # choose individually
        for abspath, mbsize in largefiles.items():
            stats = f'{abspath.relative_to(cwd)} ({mbsize}MB)'
            misc.whiteprint(stats)
            key, answer = prompt.action(f'Handling: {abspath}',
                                        'ignore',
                                        'split to subfiles (checks for pre-existing beforehand)',
                                        flowopts=True)
            if key == 'i':
                ignore(abspath.relative_to(cwd), dry_run=dry_run)
            elif key == 's':
                _split_file(abspath, cwd, dry_run)


def get_large_files_from_status(cwd, status: Status) -> Dict[ExPath, float]:
    largefiles = {}
    for f in status.files:
        statuce = status.file_status_map[f]
        if 'D' in statuce:
            continue
        
        # TODO: check if already in gitignore and just not removed from cache
        abspath = cwd / f
        mb = 0
        if abspath.exists():
            if abspath.is_dir():
                large_subfiles = _get_large_files_in_dir(abspath)
                largefiles.update(large_subfiles)
            else:
                mb = abspath.lstat().st_size / 1000000
        else:
            misc.yellowprint(f'does not exist: {repr(abspath)}')
        if mb >= 50:
            largefiles[abspath] = mb
    return largefiles


@click.command()
@click.argument('commitmsg', required=False)
@unrequired_opt('-n', '--dry-run', is_flag=True)
def main(commitmsg: str, dry_run: bool = False):
    status = Status()
    if not status.files:
        if prompt.confirm('No files in status, just push?'):
            if dry_run:
                misc.whiteprint('dry run, not pushing. returning')
                return
            return git.push()
    
    cwd = ExPath(os.getcwd())
    
    largefiles: Dict[ExPath, float] = get_large_files_from_status(cwd, status)
    if largefiles:
        handle_large_files(cwd, largefiles, dry_run)
    
    if not commitmsg:
        if len(status.files) == 1:
            commitmsg = status.files[0]
        elif len(status.files) < 3:
            commitmsg = ', '.join([f.name for f in status.files])
        else:
            os.system('git status -s')
            commitmsg = input('commit msg:\t')
    commitmsg = misc.unquote(commitmsg)
    if dry_run:
        misc.whiteprint('dry run. exiting')
        return
    shell.run('git add .',
              f'git commit -am "{commitmsg}"')
    git.push()


if __name__ == '__main__':
    try:
        main()
    except FileNotFoundError as e:
        print(colors.brightred(repr(e)))
        raise e
