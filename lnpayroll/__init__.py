import importlib.metadata

__version__ = importlib.metadata.version("lnpayroll")

from lnpayroll.lib import *
from lnpayroll.exchange import *
from lnpayroll.exceptions import *
