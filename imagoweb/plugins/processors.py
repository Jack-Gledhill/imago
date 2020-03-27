# ========================
# Import PATH dependencies
# ========================
# ------------------------
# Third-party dependencies
# ------------------------
from flask import request, Response

# ======================
# Import local libraries
# ======================
from imagoweb.util.constants import app, const
from imagoweb.util.utilities import get_user

@app.context_processor
def inject_globals():
    """Allows the user variable to be retrieved from all views.
    
    Effectively, this means that every page can easily access the user variable."""

    return dict(version=dict(const.version))