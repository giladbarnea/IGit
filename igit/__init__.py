import sys
from IPython.core import ultratb

sys.excepthook = ultratb.VerboseTB(include_vars=True)
print('excepthook: VerboseTB')
