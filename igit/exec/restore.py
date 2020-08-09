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
        key, answer = prompt.action('What to do?', 'restore all files', 'choose files', flowopts=('debug', 'quit'))
        if key == 'r':
            restoreall = True
        elif answer == 'c':
            status = Status()
            idx, choice = prompt.choose('which?', *status.files, flowopts='quit', free_input=True)
            if idx is None:
                # free input
                restore = status.search(choice, noprompt=False)
            else:
                restore = status.files[idx]
    
    # util.clip_copy(branch)


if __name__ == '__main__':
    main()
