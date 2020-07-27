# Copyright (C) JackTEK 2018-2020
# -------------------------------

# ========================
# Import PATH dependencies
# ========================
# ------------------------
# Third-party dependencies
# ------------------------
from flask import request, Response

# -------------------------
# Local extension libraries
# -------------------------
from util.constants import app, config, version


@app.context_processor
def inject_globals():
    """Allows the user variable to be retrieved from all views.
    
    Effectively, this means that every page can easily access the user variable."""

    return dict(version=dict(version),
                len=len,
                enumerate=enumerate)