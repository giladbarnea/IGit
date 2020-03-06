#!/usr/bin/env python3.7

from mytool import git
import webbrowser
import click


@click.command()
@click.argument("commit_index", required=False)
def main(commit_index):
    current = git.commit.current()
    webbrowser.open(f"https://{git.repourl()}/branches/compare/{current}%0D{git.branch.current()}#diff")


if __name__ == '__main__':
    main()
