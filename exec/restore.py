#!/usr/bin/env python3.8
import click

import os

import prompt
from status import Status


@click.command()
@click.argument('index_or_substr', required=False)
def main(index_or_substr):
    restoreall = False
    if not index_or_substr:
        os.system('git status -s')
        answer = prompt.action('What to do?', 'restore all file', C='choose files', special_opts=True)
        if answer == 'y':
            restoreall = True
        elif answer == 'c':
            status = Status()
            answer = prompt.choose('which?', status.files, 'quit', allow_free_input=True)
            if answer.isdigit():
                restore = status.files[int(answer)]
            else:
                restore = status.search(answer)
    
    # util.clip_copy(branch)


if __name__ == '__main__':
    main()
