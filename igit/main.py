#!/usr/bin/env python3.8
from prompt_toolkit import prompt as ptprompt, print_formatted_text, HTML, formatted_text, PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import os

from igit.branches import Branches
from igit.commits import Commits
from igit.repo import Repo


def bottom_toolbar():
    return btree.current


btree = Branches()
ctree = Commits()
repo = Repo()

uname = os.getlogin()
session = PromptSession(clipboard=True)
# prompt_continuation? input_preprocessors, erase_when_done, inputhook, input, output
# style = Style([('prompt', '#3c055a bold'), ])
style = Style([('prompt', '#00AFF9 bold'), ])
completer = WordCompleter([f'%{a}' for a in ['a',  # add
                                             'br',  # branch
                                             'c',  # commit
                                             'co',  # checkout
                                             'f',  # fetch
                                             'l',  # log
                                             'p',  # push
                                             'pl',  # pull
                                             'm',  # merge
                                             'st',  # status
                                             ]])


def get_rprompt():
    return ctree.current


while True:
    # default, accept_default, pre_run
    text = session.prompt(
            [('class:prompt', f'{uname}@{repo.name} ')],
            auto_suggest=AutoSuggestFromHistory(),
            style=style,
            completer=completer,
            complete_while_typing=True,
            bottom_toolbar=bottom_toolbar,
            rprompt=get_rprompt()
            )
    if text in ('q', 'quit'):
        break
# print_formatted_text(HTML("<prompt>>>></prompt>"), style=style)
