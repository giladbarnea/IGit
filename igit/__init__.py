import sys
from IPython.core import ultratb
from ipdb import set_trace

sys.excepthook = ultratb.VerboseTB(include_vars=True)
print('sys.excepthook = VerboseTB')
sys.breakpointhook = set_trace
