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
from imagoweb.util.constants import app, cache, config, const
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
                                                       condition=lambda url: url.owner_id == user.user_id)),
                                          messages=len(all(iterable=cache.messages,
                                                           condition=lambda msg: msg.recipient_id == user.user_id))))

@app.route(rule="/messages")
@app.route(rule="/home/messages")
def messaging_page():
    """Displays a list of system messages sent to the user."""

    user = check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    return render_template(template_name_or_list="home/messages.html",
                           user=user,
                           superuser=const.superuser,
                           nav_stats=dict(files=len(all(iterable=cache.files,
                                                        condition=lambda file: file.owner_id == user.user_id)),
                                          urls=len(all(iterable=cache.urls,
                                                       condition=lambda url: url.owner_id == user.user_id)),
                                          messages=len(all(iterable=cache.messages,
                                                           condition=lambda msg: msg.recipient_id == user.user_id))),
                           messages=all(iterable=cache.messages,
                                        condition=lambda msg: msg.recipient_id == user.user_id))

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
                                                       condition=lambda url: url.owner_id == user.user_id)),
                                          messages=len(all(iterable=cache.messages,
                                                           condition=lambda msg: msg.recipient_id == user.user_id))))

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
                                                       condition=lambda url: url.owner_id == user.user_id)),
                                          messages=len(all(iterable=cache.messages,
                                                           condition=lambda msg: msg.recipient_id == user.user_id))))

@app.route(rule="/urls/new")
@app.route(rule="/home/urls/new")
def new_url():
    """Allows a user to shorten a URL from the dashboard."""

    user = check_user(token=request.cookies.get("_auth_token"))

    if user is None:
        return redirect(location="/api/login",
                        code=303), 303

    return render_template(template_name_or_list="home/new.html",
                           user=user,
                           can_custom_name=(user.is_admin and config.url_shortening.custom_url.admin_only) or not config.url_shortening.custom_url.admin_only,
                           nav_stats=dict(files=len(all(iterable=cache.files,
                                                        condition=lambda file: file.owner_id == user.user_id)),
                                          urls=len(all(iterable=cache.urls,
                                                       condition=lambda url: url.owner_id == user.user_id)),
                                          messages=len(all(iterable=cache.messages,
                                                           condition=lambda msg: msg.recipient_id == user.user_id))))