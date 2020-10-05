import os
from functools import partial

from time import perf_counter

ts0 = perf_counter()

from igit_debug.loggr import Loggr

ts1 = perf_counter()
print(f'igit.__init__.py | importing Loggr took {round((ts1 - ts0) * 1000, 2)}ms')  # 54.18ms because of import logbook
logger = Loggr()
ts2 = perf_counter()
print(f'igit.__init__.py | logger=Loggr() took {round((ts2 - ts1) * 1000, 2)}ms')


def extend_print():
    """
    >>> print.red('hi')
    \x1b[31mhi\x1b[39m
    """
    # "replace" print with ours. needed because otherwise can't `__builtins__.print.red = ...`
    from copy import deepcopy
    import more_termcolor
    _print_copy = deepcopy(__builtins__['print'])
    _print = lambda *args, **kwargs: _print_copy(*args, **kwargs)
    
    def cprint(_colorfn, *args, **kwargs):
        print(_colorfn(*args, **kwargs))
    
    for colorfn_name in filter(lambda attr: not str(attr).startswith('__'), dir(more_termcolor.colors)):
        colorfn = getattr(more_termcolor.colors, colorfn_name)
        
        _print.__dict__[colorfn_name] = partial(cprint, colorfn)
    
    __builtins__['print'] = _print
    logger.debug('finished extending print')


def do_debug_patching():
    import sys
    
    from IPython.core import ultratb
    from ipdb import set_trace
    
    from igit.util.misc import is_pycharm
    
    # TODO: learn how to call pdb on exception just using ipdb, not relying on ipython
    #  (currently, whenever calling ipdb, it uses ipython → startup scripts → igit)
    #  this will enable having env vars IGIT_CALL_PDB=TRUE and IGIT_MODE="" and still
    #  calling pdb on exception (right now they're dependent)
    IGIT_CALL_PDB = eval(os.environ.get('IGIT_CALL_PDB', ''))
    IGIT_EXCEPTHOOK = os.environ.get('IGIT_EXCEPTHOOK', '')
    using_pycharm = is_pycharm()
    actually_call_pdb = IGIT_CALL_PDB and not using_pycharm
    
    logger.info('IGIT_MODE == DEBUG',
                'IGIT_CALL_PDB:', IGIT_CALL_PDB,
                'actually calling pdb:', actually_call_pdb,
                'IGIT_EXCEPTHOOK:', IGIT_EXCEPTHOOK,
                'using_pycharm:', using_pycharm)
    
    if IGIT_EXCEPTHOOK == 'VerboseTB':
        sys.excepthook = ultratb.VerboseTB(include_vars=True, call_pdb=actually_call_pdb)
    
    if actually_call_pdb:
        sys.breakpointhook = partial(set_trace, context=30)


ts3 = perf_counter()
extend_print()
ts4 = perf_counter()
print(f'igit.__init__.py | extend_print() took {round((ts4 - ts3) * 1000, 2)}ms')

IGIT_MODE = os.environ.get('IGIT_MODE', '')
logger.debug(f'IGIT_MODE: {repr(IGIT_MODE)}')
if IGIT_MODE == 'DEBUG':
    ts5 = perf_counter()
    do_debug_patching()
    ts6 = perf_counter()
    print(f'igit.__init__.py | do_debug_patching() took {round((ts6 - ts5) * 1000, 2)}ms')
