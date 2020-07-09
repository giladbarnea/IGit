import sys
import os
from functools import partial

from IPython.core import ultratb
from ipdb import set_trace

from igit.util.misc import is_pycharm

call_pdb = os.environ.get('IGIT_CALL_PDB', 'FALSE') == 'TRUE'
sys.excepthook = ultratb.VerboseTB(include_vars=True, call_pdb=call_pdb or is_pycharm())
print('sys.excepthook = VerboseTB')

sys.breakpointhook = partial(set_trace, context=30)
