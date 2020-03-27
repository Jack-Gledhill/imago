# ========================
# Import PATH dependencies
# ========================
# ------------------------
# Third-party dependencies
# ------------------------
from flask import abort, jsonify, render_template, request, redirect
from datetime import datetime

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

@app.route(rule="/admin/images")
@app.route(rule="/home/admin/images")
def gallery_page():
    """This displays the images section of the admin panel."""

    user = check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    if not user.is_admin:
        abort(status=403)

    return render_template(template_name_or_list="admin/images.html",
                           user=user,
                           superuser_id=const.superuser.user_id,
                           superuser=user.api_token == const.superuser.api_token,
                           images=cache.images)

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