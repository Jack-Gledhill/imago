# ===================
# Import dependencies
# ===================
# -----------------
# Builtin libraries
# -----------------
import typing

from collections import namedtuple
from datetime import datetime

# ------------------------
# Third-party dependencies
# ------------------------
from attrdict import AttrDict
from custos import version, blueprint
from yaml import safe_load

# ======================
# Import local libraries
# ======================
from imagoweb.util.blueprints import user

config = AttrDict(safe_load(open(file="config.yml",
                                 mode="r")))

const = AttrDict(dict(boot_dt=datetime.utcnow(),
                      version=version(major=config.version.major,
                                      minor=config.version.minor,
                                      patch=config.version.patch,
                                      release=config.version.release),
                      superuser=user(username=config.superuser.username,
                                     password=config.superuser.password,

                                     display_name=config.superuser.display_name,
                                     created_at=datetime.utcnow(),

                                     token=config.superuser.api_token,
                                     admin=True,
                                     id=0)))

cache = namedtuple(typename="cache", 
                   field_names="images, users")(images=[], 
                                                users=[const.superuser])

epoch = datetime(year=2000,
                 month=1,
                 day=1,
                 hour=0,
                 minute=0,
                 second=1)