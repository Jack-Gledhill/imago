# =====================
# Import PATH libraries
# =====================
# -----------------
# Builtin libraries
# -----------------
from os import _exit
from datetime import datetime

# ------------------------
# Third-party dependencies
# ------------------------
try:
    from custos import Custos

except ImportError:
    now = datetime.utcnow()
    
    print(f"{now.strftime('%d-%m-%Y')} {now.strftime(format='%H:%M:%S')}:{str(round(number=int(now.strftime(format='%f'))/1000)).rjust(3, '0')} \x1b[31mFATAL\x1b[0m  [\x1b[32mimago:\x1b[0m\x1b[34mutil.init\x1b[0m]: custos dependency is missing.")

    _exit(status=2)

# --------------------------
# Import extension libraries
# --------------------------
from .constants import *

console = Custos(project_name="imago",
                 log_level=config.logging.level)