# Copyright (C) JackTEK 2018-2020
# -------------------------------

# ========================
# Import PATH dependencies
# ========================
# -----------------
# Builtin libraries
# -----------------
import os.path

from datetime import datetime
from re import match
from os import remove, rename, replace

# ------------------------
# Third-party dependencies
# ------------------------
from flask import abort, make_response, render_template, request, redirect, jsonify

# -------------------------
# Local extension libraries
# -------------------------
import util.utilities as utils

from util.blueprints import File, URL, User
from util.constants import app, cache, config, const, epoch, markdown, postgres


BASE = "/api"

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
        return utils.respond(code=422,
                             msg="Missing JSON data.")

    id = request.json.get("id")
    password = request.json.get("password")

    if None in (id, password):        
        return utils.respond(code=422,
                             msg="Missing JSON data.")

    user = utils.get_user(token_or_id=id)

    if user is None:
        return utils.respond(code=404,
                             msg="Invalid user ID.")

    if user.password != password:
        return utils.respond(code=403,
                             msg="Password is not correct.")

    return utils.respond(code=200,
                         msg="Password is correct.")

@app.route(rule=BASE + "/authenticate",
           methods=["POST"])
def authenticate():
    """Queries the provided username and password to fetch a user."""

    if not request.is_json:
        return utils.respond(code=422,
                             msg="Missing JSON data.")

    username = request.json.get("username")
    password = request.json.get("password")

    if None in (username, password):        
        return utils.respond(code=422,
                             msg="Missing JSON data.")

    if username == const.superuser.username and password == const.superuser.password:
        return utils.respond(**dict(const.superuser))

    user = utils.first(iterable=cache["users"],
                       condition=lambda user: user.username == username and user.password == password)

    if user is None:
        return utils.respond(code=404,
                             msg="User not found.")

    return utils.respond(**dict(user))

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

    return res

@app.route(rule=BASE + "/login")
def login():
    """Sends the user to the login screen."""

    if utils.check_user(token=request.headers.get("Authorization")) is None:
        return render_template(template_name_or_list="login.html"), 200

    return redirect(location="/home",
                    code=303), 303

@app.route(rule=BASE + "/shorten",
           methods=["POST"])
def shorten_url():
    """Takes a URL and shortens it. This is useful for particularly long URLs like Google Form links."""

    user = utils.check_user(token=request.headers.get("Authorization"))

    if user is None:
        return utils.respond(code=403,
                             msg="Invalid API token.")

    if not request.is_json:
        return utils.respond(code=403,
                             msg="Missing JSON data.")

    to_shorten = request.json.get("url")

    if to_shorten is None:
        return utils.respond(code=403,
                             msg="Missing JSON data.")

    found_url = utils.first(iterable=cache["urls"],
                            condition=lambda url: url.url == to_shorten)

    if found_url:
        return utils.respond(code=409,
                             msg="That URL has already been shortened.",
                             link=f"https://{request.url_root.lstrip('http://')}u/{found_url.key}")

    if match(pattern=URL_REGEX,
             string=to_shorten) is None:
        return utils.respond(code=403,
                             msg="That URL is invalid.")

    key = request.headers.get("URL-Name")

    if not (user.admin and config.url_shortening.custom_url.admin_only) or not key:
        key = utils.generate_key(cache_obj="urls")

    with postgres.cursor() as con:
        query = """INSERT INTO urls (owner_id, key, url, created_at)
                   VALUES (%(owner_id)s, %(key)s, %(url)s, %(created_at)s)
                   
                   RETURNING id;"""

        con.execute(query,
                    dict(owner_id=user.id,
                         key=key,
                         url=to_shorten,
                         created_at=datetime.utcnow()))

        url_id = con.fetchone()[0]
        url_obj = URL(id=url_id,
                      key=key,
                      url=to_shorten,
                      created_at=datetime.utcnow(),
                      owner=user)

        cache["urls"].insert(0, url_obj)

    return f"https://{request.url_root.lstrip('http://')}u/{key}", 200

@app.route(rule=BASE + "/upload",
           methods=["POST"])
def upload_file():
    """This allows a user to upload any sort of file to the server."""

    user = utils.check_user(token=request.headers.get("Authorization"))

    if user is None:
        return utils.respond(code=403,
                             msg="Invalid API token.")

    file = request.files.get("upload")

    if file is None:
        return utils.respond(code=422,
                             msg="Missing file data.")

    file_type = utils.filetype(filename=file.filename)

    if file_type is False:
        return utils.respond(code=422,
                             msg="Invalid filetype")

    key = f"{utils.generate_key()}.{file.filename.rsplit('.', 1)[1].lower()}"

    file.save(f"static/uploads/{key}")

    if file_type == "image" and not utils.bypass_optimise(header=request.headers.get("Compression-Bypass"),
                                                          user=user):
        utils.optimise_image(key=key)

    with postgres.cursor() as con:
        query = """INSERT INTO files (owner_id, key, created_at)
                   VALUES (%(owner_id)s, %(key)s, %(created_at)s)
                   
                   RETURNING id;"""

        con.execute(query,
                    dict(owner_id=user.id,
                         key=key,
                         created_at=datetime.utcnow()))

        file_id = con.fetchone()[0]
        file_obj = File(id=file_id,
                        key=key,
                        created_at=datetime.utcnow(),
                        owner=user,
                        deleted=False)

        cache["files"].insert(0, file_obj)

    return f"https://{request.url_root.lstrip('http://')}{'f' if file_type != 'image' else 'i'}/{key}", 200

@app.route(rule=BASE + "/delete/u/<url_key>",
           methods=["DELETE", "POST"])
def delete_url(url_key: str):
    """Deletes a URL with a given key.
    
    This runs a check on the user's token to see if they're allowed to delete the file."""

    user = utils.check_user(token=request.headers.get("Authorization"))

    if user is None:
        return utils.respond(code=403,
                             msg="Invalid API token.")

    found_url = utils.first(iterable=cache["urls"],
                            condition=lambda url: url.key == url_key)
    
    if found_url is None:
        return utils.respond(code=404,
                             msg="URL not found.")

    # ========================================================
    # - User isn't admin and isn't trying to delete their file
    # - Both admin but user is not superuser
    # ========================================================
    if (not user.admin and user.id != found_url.owner.id) \
       or (user.admin and found_url.owner.admin and user.id != found_url.owner.id and user.id != const.superuser.id):
        return utils.respond(code=403,
                             msg="You don't own this URL.")

    with postgres.cursor() as con:
        query = """DELETE FROM urls
                   WHERE key = %(key)s;"""

        con.execute(query,
                    dict(key=url_key))

    cache["urls"].remove(found_url)

    return utils.respond(code=200,
                         msg="URL has been deleted.")

@app.route(rule=BASE + "/delete/f/<filename>",
           methods=["DELETE", "POST"])
def delete_file(filename: str):
    """Deletes a file with a given filename.
    
    This runs a check on the user's token to see if they're allowed to delete the file."""

    user = utils.check_user(token=request.headers.get("Authorization"))

    if user is None:
        return utils.respond(code=403,
                             msg="Invalid API token.")

    file = utils.first(iterable=cache["files"],
                       condition=lambda file: file.key == filename)
    
    if file is None:
        return utils.respond(code=404,
                             msg="File not found.")

    # ========================================================
    # - User isn't admin and isn't trying to delete their file
    # - Both admin but user is not superuser
    # ========================================================
    if (not user.admin and user.id != file.owner.id) \
       or (user.admin and file.owner.admin and user.id != file.owner.id and user.id != const.superuser.id):
        return utils.respond(code=403,
                             msg="You don't own this file.")
    with postgres.cursor() as con:
        query = """DELETE FROM files
                    WHERE key = %(key)s;"""

        con.execute(query,
                    dict(key=filename))

    os.remove(path=f"static/uploads/{filename}")
    cache["files"].remove(file)

    return utils.respond(code=200,
                         msg="File has been deleted.")

@app.route(rule=BASE + "/u/<link>")
@app.route(rule="/u/<link>")
def get_link(link: str):
    """Redirects a user to a shortened URL if it exists."""

    found_url = utils.first(iterable=cache["urls"],
                            condition=lambda url: url.key == link)

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

    file_type = utils.filetype(filename=filename)

    if file_type == "gif":
        file_type = "image"

    if file_type == "text":
        with open(file=path) as file:
            content = file.read()

        return render_template(template_name_or_list="files/text.html",
                               file=utils.first(iterable=cache.files,
                                                condition=lambda f: f.key == filename),
                               config=config.meta,
                               content=content,
                               size=utils.bytes_4_humans(count=os.path.getsize(filename=path)))

    if file_type == "code":
        with open(file=path) as file:
            content = file.read()

        file_ext = utils.filext(filename=filename)
        lang = {
            "py": "python",
            "js": "javascript",
            "go": "go",
            "ts": "typescript",
            "cpp": "cpp",
            "html": "html",
            "css": "css"
        }.get(file_ext)

        return render_template(template_name_or_list="files/code.html",
                               file=utils.first(iterable=cache.files,
                                                condition=lambda f: f.key == filename),
                               config=config.meta,
                               content=markdown(f"```{lang}\n{content}\n```"),
                               size=utils.bytes_4_humans(count=os.path.getsize(filename=path)),
                               lang=lang,
                               lang_ext=file_ext)

    if file_type == "markdown":
        with open(file=path) as file:
            content = file.read()

        return render_template(template_name_or_list="files/markdown.html",
                               file=utils.first(iterable=cache.files,
                                                condition=lambda f: f.key == filename),
                               config=config.meta,
                               content=markdown(content),
                               size=utils.bytes_4_humans(count=os.path.getsize(filename=path)))

    return render_template(template_name_or_list=f"files/{file_type}.html",
                           file=utils.first(iterable=cache.files,
                                            condition=lambda f: f.key == filename),
                           config=config.meta,
                           size=utils.bytes_4_humans(count=os.path.getsize(filename=path)))

@app.route(rule=BASE + "/user/new",
           methods=["PUT", "POST"])
def new_user():
    """Creates a user with the given data.
    
    All necessary checks are performed here."""

    user = utils.check_user(token=request.headers.get("Authorization"))

    if user is None:
        return utils.respond(code=403,
                             msg="Invalid API token.")

    if not user.admin:
        return utils.respond(code=403,
                             msg="You can't create a user.",
                             needed_permission="admin")

    if not request.is_json:
        return utils.respond(code=422,
                             msg="Missing JSON data.",
                             required_fields=["username", "password", "admin"])

    if None in request.json.items():
        return utils.respond(code=422,
                             msg="Missing JSON data.")

    for key in ("username", "password", "admin"):
        if key not in request.json.keys():
            return utils.respond(code=422,
                                 msg="Missing JSON data.",
                                 required_fields=["username", "password", "admin"])
                            
    # =============================================================
    # User isn't superuser and is trying to create an admin account
    # =============================================================
    if request.json.get("admin") is not False and user.id != const.superuser.id:
        return utils.respond(code=403,
                             msg="You can't create admin users.",
                             needed_permission="superuser")

    if request.json.get("username") in (u.username for u in cache["users"]):
        return utils.respond(code=409,
                             msg="That username has already been taken.")

    stripped_values = dict(username=request.json.get("username"),
                           password=request.json.get("password"),
                           admin=request.json.get("admin"),
                           created_at=datetime.utcnow(),
                           token=utils.generate_token())

    with postgres.cursor() as con:
        query = """INSERT INTO users (username, password, admin, token, created_at)
                   VALUES (%(username)s, %(password)s, %(admin)s, %(token)s, %(created_at)s)
                   
                   RETURNING id;"""

        con.execute(query,
                    stripped_values)

        id = con.fetchone()[0]
        user_obj = User(id=id,
                        **stripped_values)

        cache["users"].append(user_obj)

    return utils.respond(code=200,
                         msg="User has been created.",
                         id=id)

@app.route(rule=BASE + "/user/delete",
           methods=["DELETE", "POST"])
def delete_user():
    """Deletes the provided user ID.
    
    All necessary checks are performed here."""

    user = utils.check_user(token=request.headers.get("Authorization"))

    if user is None:
        return utils.respond(code=403,
                             msg="Invalid API token.")

    if not request.is_json:
        return utils.respond(code=422,
                             msg="Missing JSON data.")

    victim = utils.get_user(token_or_id=request.json.get("id"))

    if victim is None:
        return utils.respond(code=422,
                             msg="Invalid user ID.")

    # ========================================================
    # - User isn't admin and isn't trying to delete themselves
    # - Victim is superuser
    # - Both admin but user is not superuser
    # ========================================================
    if (not user.admin and user.id != victim.id) \
       or (victim.id == const.superuser.id) \
       or (user.admin and victim.admin and user.id != const.superuser.id):
        return utils.respond(code=403,
                             msg="You cannot delete the user.")

    with postgres.cursor() as con:
        query = """DELETE FROM users
                   WHERE id = %(id)s;"""

        con.execute(query,
                    dict(id=victim.id))

        cache["users"].remove(victim)

    return utils.respond(code=200,
                         msg="User has been deleted.")

@app.route(rule=BASE + "/user/edit",
           methods=["PUT", "POST"])
def edit_user():
    """Edits the provided user ID.
    
    All necessary checks are performed here."""

    user = utils.check_user(token=request.headers.get("Authorization"))

    if user is None:
        return utils.respond(code=403,
                             msg="Invalid API token.")

    if not request.is_json:
        return utils.respond(code=422,
                             msg="Missing JSON data.")

    victim = utils.get_user(token_or_id=request.json.get("id"))

    if victim is None:
        return utils.respond(code=422,
                             msg="Invalid user ID.")

    # ========================================================
    # - User isn't admin and isn't trying to change themselves
    # - Victim is superuser
    # - Both admin but user is not superuser and user isn't victim
    # ========================================================
    if (not user.admin and user.id != victim.id) \
       or (victim.id == const.superuser.id) \
       or (user.admin and victim.admin and not user.id == victim.id and user.id != const.superuser.id):
        return utils.respond(code=403,
                             msg="You cannot edit that user.")

    new_stuff = request.json.get("new_values")

    if not new_stuff:
        return utils.respond(code=422,
                             msg="Missing JSON data.")

    # ==========================
    # Check if username is taken
    # ==========================
    if "username" in new_stuff:
        # --------------------------------------
        # Ignore if the victim has this username
        # --------------------------------------
        if new_stuff.get("username") in (u.username for u in cache["users"] if u.id != victim.id):
            return utils.respond(code=409,
                                 msg="Username has been taken.")

    if "admin" in new_stuff:
        # ====================================================
        # User isn't superuser and trying to set user to admin
        # ====================================================
        if user.id != const.superuser.id:
            return utils.respond(code=403,
                                 msg="You cannot create an admin user.")

        if new_stuff.get("admin") == "toggle":
            new_stuff["admin"] = not victim.admin

    new_values = dict(username=victim.username,
                      password=victim.password,
                      admin=victim.admin,
                      token=victim.token)
                      
    new_values.update(new_stuff)

    with postgres.cursor() as con:
        query = """UPDATE users
                   SET username = %(username)s,
                   password = %(password)s,
                   admin = %(admin)s,
                   token = %(token)s
                   WHERE id = %(id)s;"""

        con.execute(query,
                    dict(id=victim.id, 
                         **new_values))

        new_obj = User(id=victim.id,
                       created_at=victim.created_at,
                       **new_values)

        cache["users"][cache["users"].index(victim)] = new_obj

    return utils.respond(code=200,
                         msg="User has been edited.",
                         new_values=new_values)

@app.route(rule=BASE + "/user/reset",
           methods=["PUT", "POST"])
def reset_token():
    """Resets the API token of a given user ID.
    
    All necessary checks are performed here."""

    user = utils.check_user(token=request.headers.get("Authorization"))

    if user is None:
        return utils.respond(code=403,
                             msg="Invalid API token.")

    if not request.is_json:
        return utils.respond(code=422,
                             msg="Missing JSON data.")

    victim = utils.get_user(token_or_id=request.json.get("id"))

    if victim is None:
        return utils.respond(code=422,
                             msg="Invalid user ID.")

    # ============================================================
    # - User isn't admin and isn't trying to change themselves
    # - Victim is superuser
    # - Both admin but user is not superuser and user isn't victim
    # ============================================================
    if (not user.admin and user.id != victim.id) \
       or (victim.id == const.superuser.id) \
       or (user.admin and victim.admin and not user.id == victim.id and user.id != const.superuser.id):
        return utils.respond(code=403,
                             msg="You cannot reset that user's token.")

    new_token = utils.generate_token()
                      
    with postgres.cursor() as con:
        query = """UPDATE users
                   SET token = %(token)s
                   WHERE id = %(id)s;"""

        con.execute(query,
                    dict(token=new_token,
                         id=victim.id))

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # our task of updating the cache is easy here,
        # all we have to do is change the variable of victim
        # because the victim variable points directly to cache
        # and isn't a deep or shallow copy
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        victim.token = new_token
                          
    return utils.respond(code=200,
                         msg="Token has been reset.",
                         new_token=new_token)