import shlex
import subprocess as sp
from typing import Union, List

from igit_debug import ExcHandler
from igit.util import misc
from more_termcolor import colors


def run(*cmds: str, printout=True, printcmd=True, raiseonfail=True,
        input: bytes = None, stdout=sp.PIPE, stderr=sp.PIPE):
    # TODO: poll every second for long processes, like git clone
    outs = []
    for cmd in cmds:
        if printcmd:
            print(colors.brightblack(f'\n{cmd}', "italic"))
        try:
            runargs = dict()
            if isinstance(stdout, str):
                print(colors.yellow(f'shell.run() stdout is str, not passing it: {misc.trim_at(stdout, 60)}'))
            else:
                runargs['stdout'] = stdout
            if isinstance(stderr, str):
                print(colors.yellow(f'shell.run() stderr is str, not passing it: {misc.trim_at(stderr, 60)}'))
            else:
                runargs['stderr'] = stderr
            if input:
                runargs['input'] = input
            
            proc = sp.run(shlex.split(cmd), **runargs)
            if proc.stdout:
                out = proc.stdout.decode().strip()
            else:
                out = None
            
            if proc.stderr:
                stderr = proc.stderr.decode().strip()
                if stderr.endswith('Permission denied'):
                    raise PermissionError(stderr)
                print(colors.brightyellow(stderr))
        
        except Exception as e:
            print(colors.brightred(f'FAILED: `{cmd}`\n\tcaught a {e.__class__.__name__}. raiseonfail is {raiseonfail}.'))
            hdlr = ExcHandler(e)
            if raiseonfail:
                print(hdlr.full())
                raise e
            print(hdlr.summary())
        else:
            if out:
                if printout:
                    print(out, end='\n')
                outs.append(out)
    if outs:
        return outs[0] if len(outs) == 1 else outs
    return ''


def runquiet(*cmds: str, raiseonfail=True,
             input: bytes = None, stdout=sp.PIPE, stderr=sp.PIPE) -> Union[str, List[str]]:
    return run(*cmds, printout=False, printcmd=False, raiseonfail=raiseonfail, input=input, stdout=stdout, stderr=stderr)


def get_terminal_width():
    from IPython.utils.terminal import get_terminal_size
    return get_terminal_size()[0]
