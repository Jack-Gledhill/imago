# Copyright (C) JackTEK 2018-2020
# -------------------------------

# ========================
# Import PATH dependencies
# ========================
# ------------------------
# Third-party dependencies
# ------------------------
from flask import render_template, request, redirect

# -------------------------
# Local extension libraries
# -------------------------
import util.utilities as utils

from util.constants import app, cache, config, const


@app.route(rule="/")
@app.route(rule="/home")
def account_page():
    """Sends the user to their account page."""

    user = utils.check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    return render_template(template_name_or_list="home/account.html",
                           user=user,
                           superuser=user.id == const.superuser.id)

@app.route(rule="/files")
@app.route(rule="/home/files")
def files_page():
    """Displays a table of the user's files."""

    user = utils.check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    return render_template(template_name_or_list="home/files.html",
                           user=user,
                           files=utils.all(iterable=cache.files,
                                           condition=lambda file: file.owner.id == user.id and not file.deleted))

@app.route(rule="/urls")
@app.route(rule="/home/urls")
def shortened_urls():
    """Displays a table of the user's shortened URLs."""

    user = utils.check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    return render_template(template_name_or_list="home/urls.html",
                           user=user,
                           urls=utils.all(iterable=cache.urls,
                                          condition=lambda url: url.owner.id == user.id))

@app.route(rule="/urls/new")
@app.route(rule="/home/urls/new")
def new_url():
    """Allows a user to shorten a URL from the dashboard."""

    user = utils.check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    return render_template(template_name_or_list="home/new.html",
                           user=user,
                           can_custom_name=(user.admin and config.url_shortening.custom_url.admin_only) or not config.url_shortening.custom_url.admin_only)