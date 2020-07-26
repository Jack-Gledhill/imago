# Copyright (C) JackTEK 2018-2020
# -------------------------------

# ========================
# Import PATH dependencies
# ========================
# --------------------
# Builtin dependencies
# --------------------
import os.path

# ------------------------
# Third-party dependencies
# ------------------------
from flask import abort, jsonify, render_template, redirect, request

# -------------------------
# Local extension libraries
# -------------------------
import util.utilities as utils

from util.blueprints import File
from util.constants import app, cache, const, postgres


@app.route(rule="/admin")
@app.route(rule="/home/admin")
@app.route(rule="/home/admin/users")
def users_page():
    """This displays the users section of the admin panel."""

    user = utils.check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    if not user.admin:
        abort(status=403)

    return render_template(template_name_or_list="admin/users.html",
                           user=user,
                           superuser_id=const.superuser.id,
                           superuser=user.token == const.superuser.token,
                           users=cache.users)

@app.route(rule="/admin/files")
@app.route(rule="/home/admin/files")
def file_gallery():
    """This displays the files section of the admin panel."""

    user = utils.check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    if not user.admin:
        abort(status=403)

    return render_template(template_name_or_list="admin/files.html",
                           user=user,
                           superuser_id=const.superuser.id,
                           superuser=user.token == const.superuser.token,
                           files=utils.all(iterable=cache.files,
                                           condition=lambda file: not file.deleted))

@app.route(rule="/admin/urls")
@app.route(rule="/home/admin/urls")
def url_list():
    """This displays the shortened URLs section of the admin panel."""

    user = utils.check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    if not user.admin:
        abort(status=403)

    return render_template(template_name_or_list="admin/urls.html",
                           user=user,
                           superuser_id=const.superuser.id,
                           superuser=user.token == const.superuser.token,
                           urls=cache.urls)

@app.route(rule="/admin/new")
@app.route(rule="/home/admin/new")
def new_user_page():
    """This provides a simple form for admins to provide data for a new user."""

    user = utils.check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    if not user.admin:
        abort(status=403)

    return render_template(template_name_or_list="admin/new.html",
                           is_superuser=user.id == const.superuser.id,
                           user=user)

@app.route(rule="/admin/edit/<victim_id>")
@app.route(rule="/home/admin/edit/<victim_id>")
def edit_user_page(victim_id: int):
    """This provides a simple form for admins to edit a user."""

    user = utils.check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    victim = utils.check_user(token=victim_id)

    if victim is None:
        return jsonify(dict(code=422,
                            message="Invalid or missing user ID.")), 422

    if not user.admin:
        abort(status=403)

    return render_template(template_name_or_list="admin/edit.html",
                           victim=victim,
                           user=user)