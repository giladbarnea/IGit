import shlex
import subprocess as sp
from typing import Union, List, Literal

from igit_debug import ExcHandler
from more_termcolor import colors

from igit.util import misc
from igit.util.misc import yellowprint, brightyellowprint


def run(*cmds: str, printout=True, printcmd=True, raiseonfail: Union[bool, Literal['short', 'summary', 'full']] = True,
        input: bytes = None, stdout=sp.PIPE, stderr=sp.PIPE):
    """
    Basically a wrapper to `sp.run(shlex.split(cmd))`.
    
    Always:
     - Prints stderr (if exists) in bright yellow.
     - Uses ExcHandler if an exception occurrs
    
    :param cmds:
    :param bool printout: Print the output of each command. Default True.
    :param bool printcmd: Print the command before execution in italic bright black. Default True.
    :param raiseonfail: Regarding python exceptions, not failed commands.
      If False, suppresses exceptions, but prints their summaries.
      If True, actually raises the exception, but prints ExcHandler beforehand.
      Value can be a bool or either 'short', 'summary', 'full' to control the output of ExcHandler. True is equiv to 'full'.
      Default True.
    :param bytes input: Default None.
    :param int stdout: default sp.PIPE.
    :param int stderr: default sp.PIPE.
    :return: A string or a list of strings (stripped), depending on whether a single command or many commands were passed.
    """
    # TODO: poll every second for long processes, like git clone
    outs = []
    for cmd in cmds:
        if printcmd:
            print(colors.brightblack(f'\n{cmd}', "italic"))
        try:
            runargs = dict()
            if isinstance(stdout, str):
                yellowprint(f'shell.run() stdout is str, not passing it: {misc.trim_at(stdout, 60)}')
            else:
                runargs['stdout'] = stdout
            if isinstance(stderr, str):
                yellowprint(f'shell.run() stderr is str, not passing it: {misc.trim_at(stderr, 60)}')
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
                brightyellowprint(stderr)
        
        except Exception as e:
            print(colors.brightred(f'FAILED: `{cmd}`\n\tcaught a {e.__class__.__name__}. raiseonfail is {raiseonfail}.'))
            hdlr = ExcHandler(e)
            if raiseonfail:
                if raiseonfail is True:
                    print(hdlr.full())
                else:
                    get_trace_fn = getattr(hdlr, raiseonfail, None)
                    if get_trace_fn is None:
                        brightyellowprint(f'ExcHandler doesnt have attr: {raiseonfail}')
                    print(get_trace_fn())
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
