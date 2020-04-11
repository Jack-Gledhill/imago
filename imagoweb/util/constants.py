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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# this stops the IDE from linting errors in the code where references
# are made to these variables, it happens because the variables aren't 
# set until the main script has started and the IDE can't understand that
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
app = None
pool = None

config = AttrDict(safe_load(open(file="config.yml")))

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

locales = {
    "en-US": AttrDict(safe_load(open(file="../locales/en-US.yml"))),
    "en-UK": AttrDict(safe_load(open(file="../locales/en-UK.yml"))),
                        
    "de": AttrDict(safe_load(open(file="../locales/de.yml")))
}

cache = namedtuple(typename="cache", 
                   field_names="files, urls, users")(files=[], 
                                                     urls=[],
                                                     users=[const.superuser])

epoch = datetime(year=2000,
                 month=1,
                 day=1,
                 hour=0,
                 minute=0,
                 second=1)