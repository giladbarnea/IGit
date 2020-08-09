# Sample configurable:
from traitlets import *

from traitlets.config import PyFileConfigLoader, SingletonConfigurable, Configurable
from igit_debug.loggr import Loggr

logger = Loggr(__name__)


class User(Configurable):
    profile = Unicode(help="The user's git username")


class App(SingletonConfigurable):
    
    def __init__(self, **kwargs):
        loader = PyFileConfigLoader('igitconfig.py', path='/home/gilad/.config/igit')
        config = loader.load_config()
        super().__init__(config=config, **kwargs)
        self.user = User(parent=self)
    
    name = Unicode(u'igit', help="the name of the object").tag(config=True)
    user = Type(klass=User).tag(config=True)
    # ranking = Integer(0, help="the class's ranking").tag(config=True)
    # value = Float(99.0)
    # The rest of the class implementation would go here..
