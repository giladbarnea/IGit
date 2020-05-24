import shlex
from typing import Union, List

from igit.debug import ExcHandler
from igit.util import termcolor
import subprocess as sp


def tryrun(*cmds: str, printout=True, printcmd=True, raiseonfail=True,
           input: bytes = None, stdout=sp.PIPE, stderr=sp.DEVNULL) -> Union[str, List[str]]:
    outs = []
    for cmd in cmds:
        if printcmd:
            fmtd = termcolor.color(f'\n{cmd}', "lightgrey", "italic")
            print(fmtd)
        try:
            runargs = dict(stdout=stdout, stderr=stderr)
            # runargs = dict()
            if input:
                runargs['input'] = input
            
            proc = sp.run(shlex.split(cmd), **runargs)
            if proc.stdout:
                out = proc.stdout.decode().strip()
            else:
                out = None
        except Exception as e:
            print(termcolor.yellow(f'FAILED: {cmd}\n\tcaught a {e.__class__.__name__}. raiseonfail is {raiseonfail}.'))
            if raiseonfail:
                hdlr = ExcHandler(e)
                print(termcolor.red(hdlr.full()))
                raise e
        else:
            if out:
                if printout:
                    print(out, end='\n')
                outs.append(out)
    if outs:
        return outs[0] if len(outs) == 1 else outs
    return ''


def get_terminal_width():
    from IPython.utils.terminal import get_terminal_size
    return get_terminal_size()[0]
