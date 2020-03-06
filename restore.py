#!/usr/bin/env python3.7
import click

from mytool import util
from mytool import git
import os


@click.command()
@click.argument('index_or_substr', required=False)
def main(index_or_substr):
    restoreall = False
    if not index_or_substr:
        answer = util.ask('restore all files?', 'yes', 'choose', 'quit')
        if answer == 'y':
            restoreall = True
        elif answer == 'c':
            status = git.status()
            answer = util.choose('which?', status.files, 'quit', allow_free_input=True)
            if answer.isdigit():
                restore = status.files[int(answer)]
            else:
                restore = status.search(answer)
    
    # util.clip_copy(branch)


if __name__ == '__main__':
    main()
