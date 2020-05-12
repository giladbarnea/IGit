from typing import Union, List

from igit.debug import ExcHandler
from igit.util import termcolor
import subprocess as sp


def tryrun(*cmds: str, printout=True, printcmd=True, abortonfail=True) -> Union[str, List[str]]:
    outs = []
    for cmd in cmds:
        if printcmd:
            print(termcolor.color(f'\n{cmd}', "lightgrey", "italic"))
        try:
            out = sp.getoutput(cmd)
        except Exception as e:
            print(termcolor.yellow(f'FAILED: {cmd}\n\tcaught a {e.__class__.__name__}. abortonfail is {abortonfail}.'))
            if abortonfail:
                hdlr = ExcHandler(e)
                print(termcolor.red(hdlr.full()))
                raise e
            print(f'continuing...')
        else:
            if out:
                if printout:
                    print('\n'.join(out.splitlines()), end='\n')
                outs.append(out)
    if outs:
        return outs[0] if len(outs) == 1 else outs
    return ''
