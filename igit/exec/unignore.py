#!/usr/bin/env python3.8
import click
from igit_debug.loggr import Loggr

from igit.ignore import Gitignore


@click.command()
@click.argument('path')
def main(path):
    gitignore = Gitignore()
    gitignore.unignore(path, confirm=True)
    
    # with gitignore.open(mode='r') as f:
    #     data = [Path(line.strip()) for line in f.readlines()]
    # file = Path(file)
    # if file in data:
    #     data = sorted([str(p) for p in data if p != file])
    #     with gitignore.open(mode='w') as f:
    #         f.write('\n'.join(data))
    #     print(f'unignored {file}')
    # else:
    #     print(f'{file} not in gitignore')


if __name__ == '__main__':
    main()
