# ========================
# Import PATH dependencies
# ========================
# -----------------
# Builtin libraries
# -----------------
from typing import Any

# ------------------------
# Third-party dependencies
# ------------------------
from flask import render_template, request

# ======================
# Import local libraries
# ======================
from imagoweb.util.constants import app

@app.errorhandler(code_or_exception=403)
def forbidden(error: Any):
    """This will tell the user that they've tried to access an area beyond their authorisation level and prompt them to go back."""

    return render_template(template_name_or_list="error.html",
                           status=403), 403

@app.errorhandler(code_or_exception=404)
def page_not_found(error: Any):
    """Every time we try to visit a URI that doesn't exist, the 404 Page Not Found view is displayed.
    
    This is handy, because it allows us to make a custom error page for any error if we chose to.
    Notice how we're returning the 404 error code, this is so that clients other than browsers can understand what happened, rather than getting a 200."""

    return render_template(template_name_or_list="error.html",
                           status=404), 404

@app.errorhandler(code_or_exception=429)
def too_many_requests(error: Any):
    """Ah, the infamous 429 HTTP code.
    
    Simply put, we display an error whenever a user hits a ratelimit."""

    return render_template(template_name_or_list="error.html",
                           status=429), 429

@app.errorhandler(code_or_exception=500)
def internal_server_error(error: Any):
    """This error handler is activated when an internal server error occurs.
    
    This often happens due to programming errors, but could also be the result of an overload.
    It's a good idea to add this since the web server will fail eventually."""

    return render_template(template_name_or_list="error.html",
                           status=500), 500

@app.errorhandler(code_or_exception=503)
def unavailable_service(error: Any):
    """This error handler is activated when an unavailable service is requested.
    
    It'll often be the result of ongoing maintenance or construction within that section of the site."""

    return render_template(template_name_or_list="error.html",
                           status=503), 503