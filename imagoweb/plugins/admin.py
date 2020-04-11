# ========================
# Import PATH dependencies
# ========================
# --------------------
# Builtin dependencies
# --------------------
import os

from datetime import datetime

# ------------------------
# Third-party dependencies
# ------------------------
from flask import abort, jsonify, render_template, request, redirect

# ======================
# Import local libraries
# ======================
from imagoweb.util.constants import app, cache, const, pool
from imagoweb.util.utilities import all, check_user
from imagoweb.util.blueprints import upload

@app.route(rule="/admin")
@app.route(rule="/home/admin")
@app.route(rule="/home/admin/users")
def users_page():
    """This displays the users section of the admin panel."""

    user = check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    if not user.is_admin:
        abort(status=403)

    return render_template(template_name_or_list="admin/users.html",
                           user=user,
                           superuser_id=const.superuser.user_id,
                           superuser=user.api_token == const.superuser.api_token,
                           users=cache.users)

@app.route(rule="/admin/files")
@app.route(rule="/home/admin/files")
def file_gallery():
    """This displays the files section of the admin panel."""

    user = check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    if not user.is_admin:
        abort(status=403)

    return render_template(template_name_or_list="admin/files.html",
                           user=user,
                           superuser_id=const.superuser.user_id,
                           superuser=user.api_token == const.superuser.api_token,
                           files=all(iterable=cache.files,
                                     condition=lambda file: not file.deleted))

@app.route(rule="/admin/urls")
@app.route(rule="/home/admin/urls")
def url_list():
    """This displays the shortened URLs section of the admin panel."""

    user = check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    if not user.is_admin:
        abort(status=403)

    return render_template(template_name_or_list="admin/urls.html",
                           user=user,
                           superuser_id=const.superuser.user_id,
                           superuser=user.api_token == const.superuser.api_token,
                           urls=cache.urls)

@app.route(rule="/admin/archive")
@app.route(rule="/home/admin/archive")
def file_archive():
    """This displays all of the archived files. 
    
    Files are archived for the rest of the day when they are deleted by either the owner or an admin.
    They are then moved to separate, admin-only folder where admins can temporarily view then until they're
    permanently removed by a cronjob at midnight every day according to the host machine's local time."""

    user = check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    if not user.is_admin:
        abort(status=403)

    return render_template(template_name_or_list="admin/archive.html",
                           user=user,
                           files=all(iterable=cache.files,
                                     condition=lambda file: file.deleted and os.path.exists(f"archive/{file.discrim}")))

@app.route(rule="/new")
@app.route(rule="/home/admin/new")
def new_user_page():
    """This provides a simple form for admins to provide data for a new user."""

    user = check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    if not user.is_admin:
        abort(status=403)

    return render_template(template_name_or_list="admin/new.html",
                           is_superuser=user.user_id == const.superuser.user_id,
                           user=user)

@app.route(rule="/edit/<victim_id>")
@app.route(rule="/home/admin/edit/<victim_id>")
def edit_user_page(victim_id: int):
    """This provides a simple form for admins to edit a user."""

    user = check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    victim = check_user(token=victim_id)

    if victim is None:
        return jsonify(dict(code=422,
                            message="Invalid or missing user ID.")), 422

    if not user.is_admin:
        abort(status=403)

    return render_template(template_name_or_list="admin/edit.html",
                           victim=victim,
                           user=user)