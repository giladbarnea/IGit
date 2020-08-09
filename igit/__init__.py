import os

IGIT_MODE = os.environ.get('IGIT_MODE', '')
if IGIT_MODE == 'DEBUG':
    import sys
    from functools import partial
    
    from IPython.core import ultratb
    from ipdb import set_trace
    
    from igit.util.misc import is_pycharm, darkprint
    
    # TODO: learn how to call pdb on exception just using ipdb, not relying on ipython
    #  this will enable having env vars IGIT_CALL_PDB=TRUE and IGIT_MODE="" and still
    #  calling pdb on exception (right now they're dependent)
    IGIT_CALL_PDB = bool(os.environ.get('IGIT_CALL_PDB', ''))
    IGIT_EXCEPTHOOK = os.environ.get('IGIT_EXCEPTHOOK', '')
    using_pycharm = is_pycharm()
    if IGIT_EXCEPTHOOK == 'VerboseTB':
        sys.excepthook = ultratb.VerboseTB(include_vars=True, call_pdb=IGIT_CALL_PDB and not using_pycharm)
        
        print('\x1b[2msys.excepthook = VerboseTB (igit)\x1b[0m\n')
    
    if IGIT_CALL_PDB and not using_pycharm:
        sys.breakpointhook = partial(set_trace, context=30)
