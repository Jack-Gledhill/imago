# =====================
# Import PATH libraries
# =====================
# -----------------
# Builtin libraries
# -----------------
from os import _exit
from datetime import datetime

# -------------------------
# Local extension libraries
# -------------------------
from imagoweb.custos import Custos

from .constants import *

console = Custos(project_name="imago",
                 log_level=config.logging.level)