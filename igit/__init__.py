import sys
from IPython.core import ultratb

sys.excepthook = ultratb.VerboseTB()
print('excepthook is ultratb.VerboseTB()')
