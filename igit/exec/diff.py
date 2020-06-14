#!/usr/bin/env python3.8
import sys
from typing import Tuple

import click

from igit.ignore import Gitignore
from igit.util import shell, regex
from igit.util.clickextensions import unrequired_opt
from igit.util.path import ExPath
from more_termcolor import colors
from more_termcolor.colors import italic

tabchar = '\t'


@click.command(help=f"""Examples:\n
                    {italic(tabchar + 'diff mi-mevi-ma "[^.]*.ts"')}\n
                    {italic(tabchar + 'diff -e "js d.ts *.map"')}
                    """)
@click.argument('items', nargs=-1, required=False)
@unrequired_opt('--exclude', '-e')
def main(items: Tuple[str], exclude):
    # git diff origin/master -- . :(exclude)*.csv :(exclude)*.ipynb :(exclude)*.sql :!report_validators/*
    # or ':!*.js' ':!*.d.ts' ':!*.js.map'
    # TODO: option to view in web like comparebranch
    exclude_exts = []
    if exclude:
        for ex in exclude.split(' '):
            if ExPath(ex).exists():
                exclude_exts.append(f'":!{ex}"')
            else:
                exclude_exts.append(f'":!*.{ex}"')
    
    cmd = 'git diff --color-moved=zebra --find-copies-harder --ignore-blank-lines '
    print(colors.dark(f'items: {items}'))
    if not items:
        shell.run(cmd, stdout=sys.stdout)
    # first, *rest = items
    # if first in BranchTree():
    #     diff_files = [line.rpartition('\t')[2] for line in shell.runquiet(f"git diff --numstat {first}").splitlines()]
    # else:
    #     diff_files = [line.rpartition('\t')[2] for line in shell.runquiet(f"git diff --numstat").splitlines()]
    
    formatted = []
    # if exclude_exts:
    
    gitignore = None
    root = None
    
    for item in items:
        if regex.has_adv_regex(item):
            # for diff_file in diff_files:
            #     if re.match(item, diff_file):
            #         stripped = diff_file.strip()
            #         formatted.append(f'"{stripped}"')
            # continue
            
            if gitignore is None:
                gitignore = Gitignore()
            if root is None:
                root = ExPath('.')
            for match in root.regex(item, lambda x: not gitignore.is_ignored(x)):
                stripped = match.strip()
                formatted.append(f'"{stripped}"')
            continue
        
        stripped = item.strip()
        formatted.append(f'"{stripped}"')
    
    joined = " ".join(formatted)
    cmd += f'{joined} '
    if exclude_exts:
        cmd += " ".join(exclude_exts)
    
    shell.run(cmd, stdout=sys.stdout)


if __name__ == '__main__':
    main()
