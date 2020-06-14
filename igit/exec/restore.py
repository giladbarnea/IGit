#!/usr/bin/env python3.8
import click

import os

from igit import prompt
from igit.status import Status


@click.command()
@click.argument('index_or_substr', required=False)
def main(index_or_substr):
    restoreall = False
    if not index_or_substr:
        os.system('git status -s')
        key, answer = prompt.action('What to do?', 'restore all file', 'choose files', special_opts=('debug', 'quit'))
        if answer == 'r':
            restoreall = True
        elif answer == 'c':
            status = Status()
            choice = prompt.choose('which?', *status.files, special_opts='quit', free_input=True)
            try:
                restore = status.files[choice]
            except Exception as e:
                restore = status.search(answer)
    
    # util.clip_copy(branch)


if __name__ == '__main__':
    main()
