from typing import List

from mytool import util, git


def getall() -> List[str]:
    git.fetchall()
    lines = util.tryrun(f'git log origin/{git.branch.current()} --pretty=oneline', printout=False).splitlines()
    commits = [l.partition(' ')[0] for l in lines]
    return commits


def current() -> str:
    return util.tryrun('git rev-parse HEAD')


def last(commits: List[str] = None) -> str:
    git.fetchall()
    if not commits:
        commits = getall()
    return commits[0]
