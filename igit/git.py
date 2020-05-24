#!/usr/bin/env python3.8

import subprocess as sp


def fetchall() -> int:
    return sp.call('git fetch --all'.split())


def pull() -> int:
    # https://stackoverflow.com/questions/5136611/capture-stdout-from-a-script
    # from IPython.utils.capture import capture_output
    # with capture_output() as c: print('some output')
    # TODO: understand how to get colors AND output
    return sp.call('git pull'.split())


def push() -> int:
    # sp.check_output(shlex.split('git fetch')) == b'' when nothing to pull
    return sp.call('git push'.split())


def status() -> int:
    return sp.call('git status'.split())
