import os
from functools import partial

from igit_debug.loggr import Loggr

logger = Loggr()


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


extend_print()

IGIT_MODE = os.environ.get('IGIT_MODE', '')
if IGIT_MODE == 'DEBUG':
    
    import sys
    
    from IPython.core import ultratb
    from ipdb import set_trace
    
    from igit.util.misc import is_pycharm
    
    # TODO: learn how to call pdb on exception just using ipdb, not relying on ipython
    #  this will enable having env vars IGIT_CALL_PDB=TRUE and IGIT_MODE="" and still
    #  calling pdb on exception (right now they're dependent)
    IGIT_CALL_PDB = bool(os.environ.get('IGIT_CALL_PDB', ''))
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
