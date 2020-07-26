# Copyright (C) JackTEK 2018-2020
# -------------------------------

# ========================
# Import PATH dependencies
# ========================
# ------------
# Type imports
# ------------
from typing import Any


# ------------------------
# Third-party dependencies
# ------------------------
from flask import render_template

# -------------------------
# Local extension libraries
# -------------------------
from util.constants import app


ERRORS = {
    403: {
        "title": "403 - Forbidden",
        "emoticon": ";-;",
        "code": "403 - You're not allowed to go there",
        "brief": "Intruder alert!",
        "desc": "Oi! This is a restricted area! Clear out!"
    },
    404: {
        "title": "404 - Page not found",
        "emoticon": "¯\_( ツ )_/¯",
        "code": "404 - That page doesn't exist",
        "brief": "Walking in circles.",
        "desc": "I'm sure I've seen that rock before..."
    },
    429: {
        "title": "429 - Too many requests",
        "emoticon": "┻━┻ ﾐヽ(ಠ益ಠ)ノ彡┻━┻",
        "code": "429 - You're being ratelimited",
        "brief": "All right, what's all this then?",
        "desc": "G'day sir/madam, license & registration please?"
    },
    500: {
        "title": "500 - Internal server error",
        "emoticon": "(╯°□°)╯",
        "code": "500 - It's not you, it's us",
        "brief": "Mmm, toasted server...",
        "desc": "Uh oh... Fire in the server room!"
    },
    503: {
        "title": "503 - Service unavailable",
        "emoticon": "ﾉ(° -°ﾉ)",
        "code": "503 - This area's under maintenance",
        "brief": "Stop, hammer time!",
        "desc": "Can anyone else hear a drill?"
    },
}

_ = lambda code: (render_template(template_name_or_list="error.html",
                                  error=ERRORS.get(code)), code)

@app.errorhandler(code_or_exception=403)
def forbidden(error: Any):
    """This will tell the user that they've tried to access an area beyond their authorisation level and prompt them to go back."""

    return _(code=403)

@app.errorhandler(code_or_exception=404)
def page_not_found(error: Any):
    """Every time we try to visit a URI that doesn't exist, the 404 Page Not Found view is displayed.
    
    This is handy, because it allows us to make a custom error page for any error if we chose to.
    Notice how we're returning the 404 error code, this is so that clients other than browsers can understand what happened, rather than getting a 200."""

    return _(code=404)

@app.errorhandler(code_or_exception=429)
def too_many_requests(error: Any):
    """Ah, the infamous 429 HTTP code.
    
    Simply put, we display an error whenever a user hits a ratelimit."""

    return _(code=429)

@app.errorhandler(code_or_exception=500)
def internal_server_error(error: Any):
    """This error handler is activated when an internal server error occurs.
    
    This often happens due to programming errors, but could also be the result of an overload.
    It's a good idea to add this since the web server will fail eventually."""

    return _(code=500)

@app.errorhandler(code_or_exception=503)
def unavailable_service(error: Any):
    """This error handler is activated when an unavailable service is requested.
    
    It'll often be the result of ongoing maintenance or construction within that section of the site."""

    return _(code=503)