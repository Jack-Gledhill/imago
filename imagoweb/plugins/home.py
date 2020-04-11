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
                           superuser=user.user_id == const.superuser.user_id,
                           nav_stats=dict(files=len(all(iterable=cache.files,
                                                        condition=lambda file: file.owner_id == user.user_id)),
                                          urls=len(all(iterable=cache.urls,
                                                       condition=lambda url: url.owner_id == user.user_id))))

@app.route(rule="/files")
@app.route(rule="/home/files")
def files_page():
    """Displays a table of the user's files."""

    user = check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    return render_template(template_name_or_list="home/files.html",
                           user=user,
                           files=all(iterable=cache.files,
                                     condition=lambda file: file.owner_id == user.user_id and not file.deleted),
                           nav_stats=dict(files=len(all(iterable=cache.files,
                                                        condition=lambda file: file.owner_id == user.user_id)),
                                          urls=len(all(iterable=cache.urls,
                                                       condition=lambda url: url.owner_id == user.user_id))))

@app.route(rule="/urls")
@app.route(rule="/home/urls")
def shortened_urls():
    """Displays a table of the user's shortened URLs."""

    user = check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    return render_template(template_name_or_list="home/urls.html",
                           user=user,
                           urls=all(iterable=cache.urls,
                                    condition=lambda url: url.owner_id == user.user_id),
                           nav_stats=dict(files=len(all(iterable=cache.files,
                                                        condition=lambda file: file.owner_id == user.user_id)),
                                          urls=len(all(iterable=cache.urls,
                                                       condition=lambda url: url.owner_id == user.user_id))))