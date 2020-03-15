#!/usr/bin/env python3.7
import click
from mytool import term
from pathlib import Path
import sys

from mytool import git


@click.command()
@click.argument('files_to_ignore', nargs=-1)
def main(files_to_ignore):
    gitignore = Path('.gitignore')
    if not gitignore.is_file():
        sys.exit(term.red(f'{gitignore.absolute()} is not file'))
    paths = []
    status = git.status()
    files = status.files
    for f in files_to_ignore:
        if isinstance(f, int) or f.isdigit():
            try:
                f = files[int(f)]
            except IndexError:
                i = input(f'Index error, try again:\t')
                f = files[int(i)]
        
        path = Path(f)
        if not path.exists():
            print(term.warn(f'{path} does not exist, skipping'))
            continue
        paths.append(path)
    if not paths:
        sys.exit(term.red('no paths'))
    with open(gitignore) as f:
        read = f.read()
        if read:
            linebreak_at_eof = read[-1] == '\n'
        else:
            linebreak_at_eof = False
    
    with open(gitignore, mode='a') as f:
        start = '' if linebreak_at_eof else '\n'
        for p in paths:
            val = f'{p}/' if p.is_dir() else p
            f.write(f'{start}{val}\n')
            print(term.green(f'Added {val} to .gitignore'))


if __name__ == '__main__':
    main()
