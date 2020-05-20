from igit import prompt
import subprocess as sp
from contextlib import redirect_stdout
from prompt_toolkit import prompt, patch_stdout
from prompt_toolkit.shortcuts import confirm


def test__ask():
    p = sp.Popen(f'input("hi\t")', shell=True, executable='python3.8')
    pass
