# ========================
# Import PATH dependencies
# ========================
# -----------------
# Builtin libraries
# -----------------
import os, re

from datetime import datetime

# ------------------------
# Third-party dependencies
# ------------------------
from flask import abort, make_response, render_template, request, redirect, jsonify, url_for, send_file

# ======================
# Import local libraries
# ======================
from imagoweb.util.constants import app, cache, config, const, epoch, locales, pool
from imagoweb.util.utilities import bypass_optimise, check_user, filetype, filext, first, generate_discrim, generate_token, get_user, make_discord_log, optimise_image
from imagoweb.util.blueprints import upload, url, user

BASE = "/api"
LOCALE = locales.get(config.default_locale).api

# ~~~~~~~~~~~~~~~~~~~~~~~~
# courtesy of urlregex.com
# ~~~~~~~~~~~~~~~~~~~~~~~~
URL_REGEX = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

app.config["MAX_IMAGE_FILESIZE"] = config.max_file_size.megabytes * 1024**2 + \
                                   config.max_file_size.kilobytes * 1024

@app.route(rule=BASE + "/check",
           methods=["POST"])
def check():
    """Checks whether or not a correct password was provided to a specific user ID."""

    if not request.is_json:
        return jsonify(dict(code=422,
                            message=LOCALE.missing.JSON)), 422

    user_id = request.json.get("user_id")
    password = request.json.get("password")

    if None in (user_id, password):        
        return jsonify(dict(code=422,
                            message=LOCALE.missing.JSON)), 422

    user = get_user(token_or_id=user_id)

    if user is None:
        return jsonify(dict(code=422,
                            message=LOCALE.invalid.USER)), 422

    if user.password != password:
        return jsonify(dict(code=403,
                            message=LOCALE.invalid.PASSWORD)), 403

    return jsonify(dict(code=200,
                        message=LOCALE.success.PASSWORD)), 200

@app.route(rule=BASE + "/authenticate",
           methods=["POST"])
def authenticate():
    """Queries the provided username and password to fetch a user."""

    if not request.is_json:
        return jsonify(dict(code=422,
                            message=LOCALE.missing.JSON)), 422

    username = request.json.get("username")
    password = request.json.get("password")

    if None in (username, password):        
        return jsonify(dict(code=422,
                            message=LOCALE.missing.JSON)), 422

    if username == const.superuser.username and password == const.superuser.password:
        return jsonify(dict(const.superuser)), 200

    user = first(iterable=cache.users,
                 condition=lambda user: user.username == username and user.password == password)

    if user is None:
        return jsonify(dict(code=404,
                            message=LOCALE.not_found.USER)), 404

    return jsonify(dict(user)), 200

@app.route(rule=BASE + "/logout")
def logout():
    """Logs the user out of their account and sends them to the login screen.
    
    If they're not logged in, sends them to the login screen anyway."""

    res = make_response(redirect(location="/api/login",
                                 code=303))

    # ===========================================
    # Delete _auth_token and display_name cookies
    # ===========================================
    res.set_cookie(key="_auth_token",
                   expires=epoch)
    res.set_cookie(key="display_name", 
                   expires=epoch)

    return res

@app.route(rule=BASE + "/login")
def login():
    """Sends the user to the login screen."""

    if check_user(token=request.headers.get("Authorization")) is None:
        return render_template(template_name_or_list="login.html"), 200

    return redirect(location="/home",
                    code=303), 303

@app.route(rule=BASE + "/shorten",
           methods=["POST"])
def shorten_url():
    """Takes a URL and shortens it. This is useful for particularly long URLs like Google Form links."""

    user = check_user(token=request.headers.get("Authorization"))

    if user is None:
        return jsonify(dict(code=403,
                            message=LOCALE.invalid.TOKEN)), 403

    if not request.is_json:
        return jsonify(dict(code=403,
                            message=LOCALE.missing.JSON)), 403

    to_shorten = request.json.get("url")

    if to_shorten is None:
        return jsonify(dict(code=403,
                            message=LOCALE.missing.JSON)), 403

    found_url = first(iterable=cache.urls,
                      condition=lambda url: url.url == to_shorten)

    if found_url:
        return jsonify(dict(code=403,
                            message=LOCALE.invalid.URL_EXISTS,
                            link=f"https://{request.url_root.lstrip('http://')}u/{found_url.discrim}")), 403

    if re.match(pattern=URL_REGEX,
                string=to_shorten) is None:
        return jsonify(dict(code=403,
                            message=LOCALE.invalid.URL)), 403

    discriminator = request.headers.get(config.url_shortening.custom_url.header)

    if not (user.is_admin and config.url_shortening.custom_url.admin_only) or not discriminator:
        discriminator = generate_discrim(cache_obj="urls")

    with pool.cursor() as con:
        query = """INSERT INTO shortened_urls (owner_id, discriminator, url, created_at)
                   VALUES (%(owner_id)s, %(discrim)s, %(url)s, %(created_at)s)
                   
                   RETURNING id;"""

        con.execute(query,
                    dict(owner_id=user.user_id,
                         discrim=discriminator,
                         url=to_shorten,
                         created_at=datetime.utcnow()))

        url_id = con.fetchone()[0]

        cache.urls.insert(0, url(id=url_id,
                                 owner_id=user.user_id,
                                 discrim=discriminator,
                                 url=to_shorten,
                                 created_at=datetime.utcnow(),
                                 owner=user))

    return_url = f"https://{request.url_root.lstrip('http://')}u/{discriminator}"

    make_discord_log(event="URL_SHORTEN",
                     user=user.display_name,
                     url=return_url,
                     link=to_shorten)

    return return_url, 200

@app.route(rule=BASE + "/upload",
           methods=["POST"])
def upload_file():
    """This allows a user to upload any sort of file to the server."""

    user = check_user(token=request.headers.get("Authorization"))

    if user is None:
        return jsonify(dict(code=403,
                            message=LOCALE.invalid.TOKEN)), 403

    file = request.files.get("upload")

    if file is None:
        return jsonify(dict(code=422,
                            message=LOCALE.missing.FILE)), 422

    file_type = filetype(filename=file.filename)

    if file_type is False:
        return jsonify(dict(code=422,
                            message=LOCALE.invalid.FILETYPE)), 422

    discriminator = f"{generate_discrim()}.{file.filename.rsplit('.', 1)[1].lower()}"

    file.save(f"static/uploads/{discriminator}")

    if file_type == "image" and not bypass_optimise(header=request.headers.get(config.file_optimisation.admin_bypass.header),
                                                    user=user):
        optimise_image(discriminator=discriminator)

    with pool.cursor() as con:
        query = """INSERT INTO uploaded_files (owner_id, discriminator, created_at)
                   VALUES (%(owner_id)s, %(discrim)s, %(created_at)s)
                   
                   RETURNING id;"""

        con.execute(query,
                    dict(owner_id=user.user_id,
                         discrim=discriminator,
                         created_at=datetime.utcnow()))

        file_id = con.fetchone()[0]

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # since we're always inserting new files to the front of the file cache,
        # the files will always be in descending order of creation time
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        cache.files.insert(0, upload(id=file_id,
                                     owner_id=user.user_id,
                                     discrim=discriminator,
                                     created_at=datetime.utcnow(),
                                     owner=user,
                                     deleted=False))

    url = f"https://{request.url_root.lstrip('http://')}{'f' if file_type != 'image' else 'i'}/{discriminator}"

    make_discord_log(event="FILE_UPLOAD",
                     user=user.display_name,
                     url=url)

    return url, 200

@app.route(rule=BASE + "/restore/<filename>",
           methods=["POST"])
def restore_file(filename: str):
    """Restores a previously deleted file with a given filename.
    
    This runs a check on the user's token to see if they're allowed to restore the file.
    Only admins are allowed to restore files to prevent abuse."""

    user = check_user(token=request.headers.get("Authorization"))

    if user is None:
        return jsonify(dict(code=403,
                            message=LOCALE.invalid.TOKEN)), 403

    # ====================
    # Check if file exists
    # ====================
    file = first(iterable=cache.files,
                  condition=lambda file: file.discrim == filename)
    
    if file is None:
        return jsonify(dict(code=404,
                            message=LOCALE.not_found.FILE)), 404

    if not user.is_admin:
        return jsonify(dict(code=403,
                            message=LOCALE.no_perms.FILE)), 403

    os.rename(src=f"archive/{filename}",
              dst=f"static/uploads/{filename}")

    with pool.cursor() as con:
        query = """UPDATE uploaded_files
                   SET deleted = false
                   WHERE discriminator = %(discrim)s;"""

        con.execute(query,
                    dict(discrim=filename))

    file.deleted = False

    cache.files[cache.files.index(file)] = file

    make_discord_log(event="FILE_RESTORE",
                     user=file.owner.display_name,
                     admin=user.display_name,
                     url=f"https://{request.url_root.lstrip('http://')}{filename}")

    return jsonify(dict(code=200,
                        message=LOCALE.success.RESTORE_FILE)), 200

@app.route(rule=BASE + "/delete/u/<url_discrim>",
           methods=["DELETE", "POST"])
def delete_url(url_discrim: str):
    """Deletes a URL with a given discriminator.
    
    This runs a check on the user's token to see if they're allowed to delete the file."""

    user = check_user(token=request.headers.get("Authorization"))

    if user is None:
        return jsonify(dict(code=403,
                            message=LOCALE.invalid.TOKEN)), 403

    # ===================
    # Check if URL exists
    # ===================
    found_url = first(iterable=cache.urls,
                      condition=lambda url: url.discrim == url_discrim)
    
    if found_url is None:
        return jsonify(dict(code=404,
                            message=LOCALE.not_found.URL)), 404

    # ========================================================
    # - User isn't admin and isn't trying to delete their file
    # - Both admin but user is not superuser
    # ========================================================
    if (not user.is_admin and user.user_id != found_url.owner_id) \
       or (user.is_admin and found_url.owner.is_admin and user.user_id != found_url.owner_id and user.user_id != const.superuser.user_id):
        return jsonify(dict(code=403,
                            message=LOCALE.no_perms.URL)), 403

    event = "URL_DELETE"

    if user.user_id != found_url.owner_id:
        event = "FORCE_URL_DELETE"

    with pool.cursor() as con:
        query = """DELETE FROM shortened_urls
                    WHERE discriminator = %(discrim)s;"""

        con.execute(query,
                    dict(discrim=url_discrim))

    cache.urls.remove(found_url)

    make_discord_log(event=event,
                     user=found_url.owner.display_name,
                     admin=user.display_name,
                     link=found_url.url)

    return jsonify(dict(code=200,
                        message=LOCALE.success.DELETE_URL)), 200

@app.route(rule=BASE + "/delete/f/<filename>",
           methods=["DELETE", "POST"])
def delete_file(filename: str):
    """Deletes a file with a given filename.
    
    This runs a check on the user's token to see if they're allowed to delete the file."""

    user = check_user(token=request.headers.get("Authorization"))

    if user is None:
        return jsonify(dict(code=403,
                            message=LOCALE.invalid.TOKEN)), 403

    # ====================
    # Check if file exists
    # ====================
    file = first(iterable=cache.files,
                  condition=lambda file: file.discrim == filename)
    
    if file is None:
        return jsonify(dict(code=404,
                            message=LOCALE.not_found.FILE)), 404

    # ========================================================
    # - User isn't admin and isn't trying to delete their file
    # - Both admin but user is not superuser
    # ========================================================
    if (not user.is_admin and user.user_id != file.owner_id) \
       or (user.is_admin and file.owner.is_admin and user.user_id != file.owner_id and user.user_id != const.superuser.user_id):
        return jsonify(dict(code=403,
                            message=LOCALE.no_perms.FILE)), 403

    event = "FILE_DELETE"

    if user.user_id != file.owner_id:
        event = "FORCE_FILE_DELETE"

    if config.file_archive.enabled:
        with pool.cursor() as con:
            query = """UPDATE uploaded_files
                       SET deleted = true
                       WHERE discriminator = %(discrim)s;"""

            con.execute(query,
                        dict(discrim=filename))

        os.replace(src=f"static/uploads/{filename}",
                   dst=f"archive/{filename}")

        file.deleted = True

        cache.files[cache.files.index(file)] = file

        make_discord_log(event=event,
                        user=file.owner.display_name,
                        admin=user.display_name,
                        url=f"https://{request.url_root.lstrip('http://')}archive/{filename}")

    else:
        with pool.cursor() as con:
            query = """DELETE FROM uploaded_files
                       WHERE discriminator = %(discrim)s;"""

            con.execute(query,
                        dict(discrim=filename))

        os.remove(path=f"static/uploads/{filename}")

        cache.files.remove(file)

        make_discord_log(event=event,
                        user=file.owner.display_name,
                        admin=user.display_name,
                        url=f"https://{request.url_root.lstrip('http://')}{filename}")

    return jsonify(dict(code=200,
                        message=LOCALE.success.DELETE_FILE)), 200

@app.route(rule=BASE + "/u/<link>")
@app.route(rule="/u/<link>")
def get_link(link: str):
    """Redirects a user to a shortened URL if it exists."""

    found_url = first(iterable=cache.urls,
                      condition=lambda url: url.discrim == link)

    if found_url is None:
        abort(status=404)

    return redirect(location=found_url.url,
                    code=303), 303

@app.route(rule=BASE + "/f/<filename>")
@app.route(rule="/f/<filename>")
@app.route(rule="/i/<filename>")
def get_file(filename: str):
    """Gets and returns an file if it exists."""

    path = f"static/uploads/{filename}"

    if not os.path.exists(path):
        abort(status=404)

    file_type = filetype(filename=filename)
    file_extension = filext(filename=filename)
    mimetype = "text/plaintext"

    if file_type in ("image", "gif"):
        mimetype = "image/{ft}"

    elif file_type == "video":
        mimetype = "video/{ft}"

    elif file_type == "audio":
        mimetype = "audio/{ft}"

    return send_file(filename_or_fp=path, 
                     mimetype=mimetype.format(ft=file_extension)), 200

@app.route(rule=BASE + "/view/archive/<filename>")
@app.route(rule="/archive/<filename>")
def get_archive(filename: str):
    """Retrieves a file from the file archive if it exists.
    
    To allow admins to see the image from their Discord servers, a webhook token is used to allow Discord to fetch the image.
    The token used must match the configuration for the webhook that receives FILE_DELETE events, since that's the event that sends the URL."""

    token = request.args.get("token")
    webhook = first(iterable=config.discord.webhooks,
                    condition=lambda hook: hook.events in ("FORCE_FILE_DELETE", "FILE_DELETE"))

    if None in (webhook, token):
        user = check_user(token=request.cookies.get("_auth_token"))

        if user is None:
            return redirect(location="/api/login",
                            code=303), 303

        if not user.is_admin:
            abort(status=403)

    elif token != webhook.get("token"):
        user = check_user(token=request.cookies.get("_auth_token"))

        if user is None:
            return redirect(location="/api/login",
                            code=303), 303

        if not user.is_admin:
            abort(status=403)

    path = f"archive/{filename}"

    if not os.path.exists(path):
        abort(status=404)

    file_type = filetype(filename=filename)
    mimetype = "text/plaintext"

    if file_type in ("image", "gif"):
        mimetype = "image/gif"

    elif file_type == "video":
        mimetype = "video/mp4"

    elif file_type == "audio":
        mimetype = "audio/mp3"

    return send_file(filename_or_fp=path, 
                     mimetype=mimetype), 200

@app.route(rule=BASE + "/user/new",
           methods=["PUT", "POST"])
def new_user():
    """Creates a user with the given data.
    
    All necessary checks are performed here."""

    perp = check_user(token=request.headers.get("Authorization"))

    if perp is None:
        return jsonify(dict(code=403,
                            message=LOCALE.missing.TOKEN)), 403

    if not perp.is_admin:
        return jsonify(dict(code=403,
                            message=LOCALE.no_perms.CREATE_USER,
                            needed_permission="admin")), 403

    if not request.is_json:
        return jsonify(dict(code=422,
                            message=LOCALE.missing.JSON,
                            required_fields=["username", "password", "display_name", "admin"])), 422

    if None in request.json.items():
        return jsonify(dict(code=422,
                            message=LOCALE.missing.JSON)), 422

    for key in ("username", "password", "display_name", "admin"):
        if key not in request.json.keys():
            return jsonify(dict(code=422,
                                message=LOCALE.missing.JSON,
                                required_fields=["username", "password", "display_name", "admin"])), 422
                            
    # =============================================================
    # User isn't superuser and is trying to create an admin account
    # =============================================================
    if request.json.get("admin") is not False and perp.user_id != const.superuser.user_id:
        return jsonify(dict(code=403,
                            message=LOCALE.no_perms.CREATE_ADMIN,
                            needed_permission="superuser")), 403

    if request.json.get("username") in (u.username for u in cache.users):
        return jsonify(dict(code=409,
                            message=LOCALE.invalid.USERNAME_TAKEN)), 409

    stripped_values = dict(username=request.json.get("username"),
                           password=request.json.get("password"),
                           display_name=request.json.get("display_name"),
                           admin=request.json.get("admin"),
                           created_at=datetime.utcnow(),
                           token=generate_token())

    with pool.cursor() as con:
        query = """INSERT INTO imago_users (username, password, display_name, admin, created_at, api_token)
                   VALUES (%(username)s, %(password)s, %(display_name)s, %(admin)s, %(created_at)s, %(token)s)
                   
                   RETURNING id;"""

        con.execute(query,
                    stripped_values)

        user_id = con.fetchone()[0]

        cache.users.append(user(id=user_id,
                                **stripped_values))

    make_discord_log(event="FORCE_USER_CREATE",
                     user=stripped_values.get("display_name"),
                     admin=perp.display_name)

    return jsonify(dict(code=200,
                        message=LOCALE.success.CREATE_USER,
                        user_id=user_id)), 200

@app.route(rule=BASE + "/user/delete",
           methods=["DELETE", "POST"])
def delete_user():
    """Deletes the provided user ID.
    
    All necessary checks are performed here."""

    user = check_user(token=request.headers.get("Authorization"))

    if user is None:
        return jsonify(dict(code=403,
                            message=LOCALE.invalid.TOKEN)), 403

    if not request.is_json:
        return jsonify(dict(code=422,
                            message=LOCALE.missing.JSON)), 422

    victim = get_user(token_or_id=request.json.get("user_id"))

    if victim is None:
        return jsonify(dict(code=422,
                            message=LOCALE.invalid.USER)), 422

    # ========================================================
    # - User isn't admin and isn't trying to delete themselves
    # - Victim is superuser
    # - Both admin but user is not superuser
    # ========================================================
    if (not user.is_admin and user.user_id != victim.user_id) \
       or (victim.user_id == const.superuser.user_id) \
       or (user.is_admin and victim.is_admin and user.user_id != const.superuser.user_id):
        return jsonify(dict(code=403,
                            message=LOCALE.no_perms.DELETE_USER)), 403

    with pool.cursor() as con:
        query = """DELETE FROM imago_users
                   WHERE id = %(user_id)s;"""

        con.execute(query,
                    dict(user_id=victim.user_id))

        cache.users.remove(victim)

    make_discord_log(event="FORCE_USER_DELETE",
                     user=victim.display_name,
                     admin=user.display_name)

    return jsonify(dict(code=200,
                        message=LOCALE.success.DELETE_USER)), 200

@app.route(rule=BASE + "/user/edit",
           methods=["PUT", "POST"])
def edit_user():
    """Edits the provided user ID.
    
    All necessary checks are performed here."""

    perp = check_user(token=request.headers.get("Authorization"))

    if perp is None:
        return jsonify(dict(code=403,
                            message=LOCALE.invalid.TOKEN)), 403

    if not request.is_json:
        return jsonify(dict(code=422,
                            message=LOCALE.missing.JSON)), 422

    victim = get_user(token_or_id=request.json.get("user_id"))

    if victim is None:
        return jsonify(dict(code=422,
                            message=LOCALE.invalid.USER)), 422

    # ========================================================
    # - User isn't admin and isn't trying to change themselves
    # - Victim is superuser
    # - Both admin but user is not superuser and user isn't victim
    # ========================================================
    if (not perp.is_admin and perp.user_id != victim.user_id) \
       or (victim.user_id == const.superuser.user_id) \
       or (perp.is_admin and victim.is_admin and not perp.user_id == victim.user_id and perp.user_id != const.superuser.user_id):
        return jsonify(dict(code=403,
                            message=LOCALE.no_perms.EDIT_USER)), 403

    new_stuff = request.json.get("new_values")

    if not new_stuff:
        return jsonify(dict(code=422,
                            message=LOCALE.missing.JSON)), 422

    # ==========================
    # Check if username is taken
    # ==========================
    if "username" in new_stuff:
        # --------------------------------------
        # Ignore if the victim has this username
        # --------------------------------------
        if new_stuff.get("username") in (u.username for u in cache.users if u.user_id != victim.user_id):
            return jsonify(dict(code=409,
                                message=LOCALE.invalid.USERNAME_TAKEN)), 409

    toggled_to = None

    if "admin" in new_stuff:
        # ====================================================
        # User isn't superuser and trying to set user to admin
        # ====================================================
        if perp.user_id != const.superuser.user_id:
            return jsonify(dict(code=403,
                                message=LOCALE.no_perms.CREATE_ADMIN)), 403

        if new_stuff.get("admin") == "toggle":
            toggled_to = new_stuff["admin"] = not victim.is_admin

    new_values = dict(username=victim.username,
                      password=victim.password,
                      display_name=victim.display_name,
                      admin=victim.is_admin,
                      token=victim.api_token)
                      
    new_values.update(new_stuff)

    with pool.cursor() as con:
        query = """UPDATE imago_users
                   SET username = %(username)s,
                   password = %(password)s,
                   display_name = %(display_name)s,
                   admin = %(admin)s,
                   api_token = %(token)s
                   WHERE id = %(user_id)s;"""

        con.execute(query,
                    dict(user_id=victim.user_id, 
                         **new_values))

        cache.users[cache.users.index(victim)] = user(id=victim.user_id,
                                                      created_at=victim.created_at,
                                                      **new_values)

    event = "USER_EDIT"
    if perp.user_id != victim.user_id:
        event = "FORCE_USER_EDIT"

    if toggled_to is not None:
        event = "ADMIN_TOGGLE_OFF"

        if toggled_to is True:
            event = "ADMIN_TOGGLE_ON"

        make_discord_log(event=event,
                         user=victim.display_name,
                         admin=perp.display_name)

    make_discord_log(event=event,
                     user=victim.display_name,
                     admin=perp.display_name)

    return jsonify(dict(code=200,
                        message=LOCALE.success.EDIT_USER,
                        new_values=new_values)), 200

@app.route(rule=BASE + "/user/reset",
           methods=["PUT", "POST"])
def reset_token():
    """Resets the API token of a given user ID.
    
    All necessary checks are performed here."""

    perp = check_user(token=request.headers.get("Authorization"))

    if perp is None:
        return jsonify(dict(code=403,
                            message=LOCALE.invalid.TOKEN)), 403

    if not request.is_json:
        return jsonify(dict(code=422,
                            message=LOCALE.missing.JSON)), 422

    victim = get_user(token_or_id=request.json.get("user_id"))

    if victim is None:
        return jsonify(dict(code=422,
                            message=LOCALE.invalid.USER)), 422

    # ============================================================
    # - User isn't admin and isn't trying to change themselves
    # - Victim is superuser
    # - Both admin but user is not superuser and user isn't victim
    # ============================================================
    if (not perp.is_admin and perp.user_id != victim.user_id) \
       or (victim.user_id == const.superuser.user_id) \
       or (perp.is_admin and victim.is_admin and not perp.user_id == victim.user_id and perp.user_id != const.superuser.user_id):
        return jsonify(dict(code=403,
                            message=LOCALE.no_perms.TOKEN_RESET)), 403

    new_token = generate_token()
                      
    with pool.cursor() as con:
        query = """UPDATE imago_users
                   SET api_token = %(token)s
                   WHERE id = %(user_id)s;"""

        con.execute(query,
                    dict(token=new_token,
                         user_id=victim.user_id))

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # our task of updating the cache is easy here,
        # all we have to do is change the variable of victim
        # because the victim variable points directly to cache
        # and isn't a deep or shallow copy
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        victim.api_token = new_token

    event = "USER_TOKEN_RESET"
    if perp.user_id != victim.user_id:
        event = "FORCE_USER_TOKEN_RESET"

    make_discord_log(event=event,
                     user=victim.display_name,
                     admin=perp.display_name)
                                        
    return jsonify(dict(code=200,
                        message=LOCALE.success.TOKEN_RESET,
                        new_token=new_token)), 200