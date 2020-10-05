#!/usr/bin/env python3.8
import sys
from typing import Tuple

import click
from more_termcolor.colors import italic

from igit.branches import Branches
from igit.commits import Commits
from igit.status import Status
from igit.util import misc
from igit import shell, regex
from igit.util.clickex import unrequired_opt
from igit.util.misc import darkprint, redprint, brightwhiteprint
from igit.search import search_and_prompt

tabchar = '\t'


@click.command(help=f"""Examples:\n
                    {italic(tabchar + 'diff mi-mevi-ma "[^.]*.ts"')}\n
                    {italic(tabchar + 'diff -e "js d.ts *.map"')}
                    """)
@click.argument('items', nargs=-1, required=False)
@unrequired_opt('--exclude', '-e')
def main(items: Tuple[str], exclude):
    # TODO: option to view in web like comparebranch
    exclude_exts = []
    if exclude:
        for ex in map(misc.clean, exclude.split(' ')):
            exclude_exts.append(misc.quote(f':!{ex}'))
    
    cmd = 'git diff --color-moved=zebra --find-copies-harder --ignore-blank-lines --ignore-cr-at-eol --ignore-space-at-eol --ignore-space-change --ignore-all-space '
    darkprint(f'diff.py main(items): {items}')
    if not items:
        # TODO: exclude
        shell.run(cmd, stdout=sys.stdout)
    
    btree = Branches()
    ctree = Commits()
    formatted = []
    # if exclude_exts:
    
    gitignore = None
    status = Status()
    
    any_sha = False
    diff_files = set()
    
    for i, item in enumerate(map(misc.clean, items)):
        if regex.SHA_RE.fullmatch(item):
            # e.g. 'f5905f1'
            any_sha = True
            if i > 1:
                redprint(f'SHA1 items, if any, must be placed at the most in the first 2 arg slots')
                return
            if item in ctree:
                if i == 1 and formatted[0] not in ctree:
                    redprint(f'When specifying two SHA1 args, both must belong to the same tree. 0th arg doesnt belong to ctree, 1st does')
                    return
                formatted.append(item)
                continue
            if item in btree:
                if i == 1 and formatted[0] not in btree:
                    redprint(f'When specifying two SHA1 args, both must belong to the same tree. 0th arg doesnt belong to btree, 1st does')
                    return
                formatted.append(item)
                continue
            redprint(f'item is SHA1 but not in commits nor branches. item: {repr(item)}')
            return
        else:
            if any_sha:
                # all SHA items have already been appended, and current item is not a SHA
                numstat_cmd = f'git diff --numstat {" ".join(items[:i])}'
            else:
                # no SHA items at all, this is the first item
                numstat_cmd = f'git diff --numstat'
            filestats = shell.runquiet(numstat_cmd).splitlines()
            diff_files = set(line.rpartition('	')[2] for line in filestats)
        
        # TODO (continue here):
        #  gpdy SHA SHA REGEX -e REGEX
        #  make -e filter out results
        
        if item in diff_files:
            with_quotes = misc.quote(item)
            formatted.append(with_quotes)
            darkprint(f'appended: {with_quotes}')
        else:
            brightwhiteprint(f'{item} is not in diff_files, searching within diff_files...')
            choice = search_and_prompt(item, diff_files)
            if choice:
                with_quotes = misc.quote(choice)
                formatted.append(with_quotes)
                darkprint(f'appended: {with_quotes}')
        
        # file = status.search(item, quiet=False)
        # if not file:
        #     brightyellowprint(f'{item} is not in status, skipping')
        #     continue
        # stripped = misc.unquote(file.strip())
        # formatted.append(misc.quote(stripped))
        # darkprint(f'appended: {repr(stripped)}')
    
    joined = " ".join(formatted)
    cmd += f'{joined} '
    if exclude_exts:
        cmd += " ".join(exclude_exts)
    
    shell.run(cmd, stdout=sys.stdout)


if __name__ == '__main__':
    main()
