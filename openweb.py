#!/usr/bin/env python3.7
from mytool import git
import webbrowser


def main():
    url = f'https://{git.repourl()}'
    # TODO: open at current branch
    webbrowser.open(url)


if __name__ == '__main__':
    main()
