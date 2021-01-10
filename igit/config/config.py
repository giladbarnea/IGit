import os

from dotenv import load_dotenv

load_dotenv(os.getenv('IGIT_ENV_FILE'))
from igit_debug.loggr import Loggr
from traitlets.config import Unicode, Configurable
from traitlets.config.loader import PyFileConfigLoader


class MyClass(Configurable):
    name = Unicode(u'defaultname', help="the name of the object").tag(config=True)
    raise_config_file_errors = True


IGIT_DIR = os.environ.get('IGIT_DIR')
cl = PyFileConfigLoader('igitconfig.py',
                        path=IGIT_DIR,
                        log=Loggr()
                        )
cfg = cl.load_config()
myinst = MyClass(config=cfg)
print(f"{myinst = }")
print(f"{myinst.name = }")
