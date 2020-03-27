# ========================
# Import PATH dependencies
# ========================
# ------------------------
# Third-party dependencies
# ------------------------
from flask import render_template, request, redirect

# ======================
# Import local libraries
# ======================
from imagoweb.util.constants import app, cache, const
from imagoweb.util.utilities import all, check_user

@app.route(rule="/")
@app.route(rule="/account")
@app.route(rule="/home")
@app.route(rule="/home/account")
def account_page():
    """Sends the user to their account page."""

    user = check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    return render_template(template_name_or_list="home/account.html",
                           user=user,
                           superuser=user.user_id == const.superuser.user_id)

@app.route(rule="/images")
@app.route(rule="/home/images")
def images_page():
    """Displays a table of the users images."""

    user = check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    return render_template(template_name_or_list="home/images.html",
                           user=user,
                           images=all(iterable=cache.images,
                                      condition=lambda image: image.owner_id == user.user_id))