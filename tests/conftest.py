import logging

from .factories import *
from .fixtures import *

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("morepath").setLevel(logging.INFO)

logg = logging.getLogger("test")
