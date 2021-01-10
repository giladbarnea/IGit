import shlex
import subprocess as sp
from typing import Union, List, Literal

from igit_debug import ExcHandler
from igit_debug.loggr import Loggr
from more_termcolor import colors

from igit.util import misc
from igit.util.misc import yellowprint, brightyellowprint

logger = Loggr()

RaiseArg = Union[bool, Literal['short', 'summary', 'full']]


def run(*cmds: str,
        printout=True,
        printcmd=True,
        raiseexc: RaiseArg = True,
        raise_on_non_zero: RaiseArg = False,
        input: bytes = None,
        stdout=sp.PIPE,
        stderr=sp.PIPE,
        **runargs):
    """
    Basically a wrapper to `subprocess.run(shlex.split(cmd))` that returns stdout(s) strings.
    
    Always:
     - Prints stderr (if exists) in bright yellow.
     - Uses ExcHandler if an exception occurrs
    
    :param cmds:
    :param bool printout: Print the output of each command. Default True.
    :param bool printcmd: Print the command before execution in italic bright black. Default True.
    :param raiseexc: Regarding python exceptions, not failed commands.
      If False, suppresses exceptions, but prints their summaries.
      If True, actually raises the exception, but prints ExcHandler beforehand.
      Value can be a bool or either 'short', 'summary', 'full' to control the output of ExcHandler. True is equiv to 'full'.
      Default True.
    :param raise_on_non_zero: If False, completely ignores returncode.
      If True, and returncode != zero, raises ChildProcessError, but prints ExcHandler beforehand.
      Value can be a bool or either 'short', 'summary', 'full' to control the output of ExcHandler. True is equiv to 'full'.
      Default False.
      Note: stderr may have content but returncode is 0, and vice-versa.
    :param bytes input: Default None.
    :param int stdout: default sp.PIPE (-1). STDOUT is -2, DEVNULL is -3.
    :param int stderr: default sp.PIPE (-1). STDOUT is -2, DEVNULL is -3.
    :param runargs: any other kwargs `subprocess.run` might accept. 'stdout', 'stderr' and 'input' are overwritten
    :return: A string or a list of strings (stripped), depending on whether a single command or many commands were passed.
      If no command had any output, returns an empty str.
    
    
    Examples:
    ::
      >>> vanilla = sp.run(shlex.split('rm does/not/exist'), stderr=sp.PIPE).stderr.decode().strip()
      >>> run('rm does/not/exist', stderr=sp.STDOUT) == vanilla
      ...
      ...
      ...
      True
    """
    # TODO: poll every second for long processes, like git clone
    outs = []
    
    for cmd in cmds:
        if printcmd:
            print(colors.brightblack(f'\n{cmd}', "italic"))
        try:
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
            
            proc: sp.CompletedProcess = sp.run(shlex.split(cmd), **runargs)
            
            if proc.stdout:
                out = proc.stdout.decode().strip()
            else:
                out = None
            
            if proc.stderr:
                stderr = proc.stderr.decode().strip()
                brightyellowprint(stderr)
            
            # keep after stderr handling so stderr is printed before raise
            if raise_on_non_zero and proc.returncode != 0:
                _handle_exception(ChildProcessError(f"shell.run() | The following command returned with code {proc.returncode}:\n{cmd}"),
                                  raise_on_non_zero,
                                  msg=f'returncode: {proc.returncode}')
        
        except Exception as e:
            _handle_exception(e, raiseexc, msg=f'FAILED: `{cmd}`\n\t{e.__class__.__name__}')
        else:
            if out:
                if printout:
                    print(out, end='\n')
                outs.append(out)
    if outs:
        return outs[0] if len(outs) == 1 else outs
    
    return ''


def _handle_exception(e: Exception, raise_arg: RaiseArg, msg: str):
    misc.brightredprint(msg, 'bold')
    hdlr = ExcHandler(e)
    if raise_arg:
        if raise_arg is True:
            print(hdlr.full())
        else:
            get_trace_fn = getattr(hdlr, raise_arg, None)
            if get_trace_fn is None:
                brightyellowprint(f'ExcHandler doesnt have fn: {raise_arg}. defaulting to `full()`')
                get_trace_fn = getattr(hdlr, 'full')
            print(get_trace_fn())
        raise e
    print(hdlr.summary())


def runquiet(*cmds: str, raiseexc=True,
             input: bytes = None, stdout=sp.PIPE, stderr=sp.PIPE) -> Union[str, List[str]]:
    """Convenience for `run(..., printout=False, printcmd=False)`"""
    return run(*cmds, printout=False, printcmd=False, raiseexc=raiseexc, input=input, stdout=stdout, stderr=stderr)


def get_terminal_width():
    from IPython.utils.terminal import get_terminal_size
    return get_terminal_size()[0]
