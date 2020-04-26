# ========================
# Import PATH dependencies
# ========================
# -----------------
# Builtin libraries
# -----------------
import os, re

from random import choice
from string import ascii_letters, digits
from typing import Union, Optional, Iterable, Any, Callable, List
from datetime import datetime

# ------------------------
# Third-party dependencies
# ------------------------
from requests import post
from PIL import Image

# =========================
# Import local dependencies
# =========================
from imagoweb.util import console
from imagoweb.util.blueprints import sysmsg, user, upload, url
from imagoweb.util.constants import cache, config, const, pool

def get_user(token_or_id: Union[str, int]) -> Union[user, None]:
    """Retrieves a user with a given API token or user ID.
    
    The token is used for backend user retrieval but also for authentication when uploading files."""

    try:
        token_or_id = int(token_or_id)
    
    except ValueError:
        pass

    if isinstance(token_or_id, str):
        key = "api_token"

    else:
        key = "id"

    if (key == "api_token" and token_or_id == const.superuser.api_token) or \
       (key == "id" and token_or_id == const.superuser.user_id):
        return const.superuser

    return first(iterable=cache.users,
                 condition=lambda user: token_or_id in (user.api_token, user.user_id))

def check_user(token: Union[str, int, None]) -> Union[user, None]:
    """Runs checks to see if a user can be retrieved from a cookie."""

    if not token:
        return None

    return get_user(token_or_id=token)

def generate_discrim(cache_obj="files"):
    """This generates a unique, available discriminator for an uploaded file."""

    # ====================
    # Generate the discrim
    # ====================
    discrim = "".join(choice(ascii_letters + digits) for i in range(config.generator.get(cache_obj)))

    # ====================================
    # Check to see if discrim is available
    # ====================================
    while discrim in [item.discrim for item in getattr(cache, cache_obj)]:
        discrim = "".join(choice(ascii_letters + digits) for i in range(config.generator.get(cache_obj)))
        
    return discrim

def generate_token():
    """This simply generates a unique, available token for a user.
    
    There's no need to worry about the superuser token here because it will always have Master at the start of it and spaces can't be generated here."""

    # ==================
    # Generate the token
    # ==================
    token = "".join(choice(ascii_letters + digits) for i in range(config.generator.token))

    # ==================================
    # Check to see if token is available
    # ==================================
    while token in [user.api_token for user in cache.users]:
        token = "".join(choice(ascii_letters + digits) for i in range(config.generator.token))
        
    return token

def filetype(filename: str) -> Union[str, bool]:
    """This checks to see if the extension of the provided filename is legal according to the configuration file.
    
    If allowed, the extension type (e.g: image) is returned. Otherwise False is returned."""

    return config.allowed_extensions.get(filext(filename=filename), False)

def filext(filename: str) -> Union[str, None]:
    """This grabs the extension of a filename. This is used to guess the MIMEtype of a file when sending it to the client."""

    if not "." in filename:
        return None

    return filename.rsplit(".", 1)[1].lower()

def first(iterable: Iterable[Any],
          condition: Callable) -> Any:
    """Returns the first item in an iterable that matches a given lambda condition.
    
    Returns None if no item matches the condition."""

    try:
        return next(item for item in iterable if condition(item))

    except StopIteration:
        return None

def all(iterable: Iterable[Any],
        condition: Callable) -> List[Any]:
    """Returns all elements that match a given condition in an iterable.
    
    Returns an empty list of no elements matched the condition."""

    return [item for item in iterable if condition(item)]

def bypass_optimise(header: str,
                    user: user) -> bool:
    """Determines whether or not the provided user can and wants to bypass image compression."""

    cfg = config.file_optimisation.admin_bypass

    if False in (cfg.can_bypass, user.is_admin):
        return False

    if not header:
        return cfg.by_default

    return True

def optimise_image(discriminator: str):
    """Takes in an file object from Flask and optimises it according to the configuration.
    
    Because the default .save function doesn't allow for optimisation kwargs, we need to save the file, 
    open it with PIL and overwrite the file with the optimised data."""

    path = f"static/uploads/{discriminator}"
    saved_file = Image.open(path)

    saved_file.save(fp=path,
                     optimize=config.file_optimisation.compress,
                     quality=config.file_optimisation.quality)

def create_sys_msg(event: str,
                   created_at: Optional[datetime] = None,
                   **msg_data: dict):
    """Sends a system message to a given user ID. 
    
    If a timestamp is not provided then the current timestamp is used."""

    content = config.sys_messaging.events.get(event)
    
    if not content or msg_data.get("recipient") is None:
        return

    content = (config.sys_messaging.before + content + config.sys_messaging.after).format(**msg_data)

    if created_at is None:
        created_at = datetime.utcnow()

    with pool.cursor() as con:
        query = """INSERT INTO system_messages (content, recipient_id, created_at)
                   VALUES (%(content)s, %(recipient_id)s, %(created_at)s)
                   
                   RETURNING id;"""

        con.execute(query,
                    dict(content=content,
                         recipient_id=msg_data.get("recipient").user_id,
                         created_at=created_at))

        msg_id = con.fetchone()

        cache.messages.append(sysmsg(id=msg_id,
                                     recipient_id=msg_data.get("recipient").user_id,
                                     content=content,
                                     created_at=created_at))

def make_discord_log(event: str,
                     **event_values: dict):
    """This sends a specific event log to Discord with the provided values.
    
    If Discord returns a 401, we internally disable Discord logging and warn the user that the token is invalid."""

    if config.discord.enabled:
        fmt = config.discord.messages.get(event)

        if fmt is None:
            return

        webhook = first(iterable=const.webhooks,
                        condition=lambda hookconfig: event in hookconfig.events)

        if webhook is None:
            return

        message = fmt.format(**event_values)

        response = post(url=webhook.url,
                        json={
                            "content": message,
                            "username": webhook.username
                        })

        # ==========================================================
        # Remove from config internally because the URL is incorrect
        # ==========================================================
        if response.status_code == 401:
            const.webhooks.remove(webhook)

        return response

def gen_hook_data(actor: user,
                  victim: Optional[user] = None,

                  before: Optional[user] = None,
                  after: Optional[user] = None,
                  
                  file: Optional[upload] = None,
                  url: Optional[url] = None,
                  
                  root_url: Optional[str] = None) -> dict:
    """Compiles a bunch of data into a dictionary that can be passed to a webhook."""

    def _compile_user(user: user) -> dict:
        return {
            "id": user.user_id,
            "name": user.username,
            "password": user.password,
            "display": user.display_name,
            "created": user.created_at_friendly,
            "admin": "Yes" if user.is_admin else "No"
        }

    compiled = {
        "actor": _compile_user(user=actor)
    }

    if victim:
        compiled["user"] = _compile_user(user=victim)

    if before:
        compiled["before"] = _compile_user(user=before)

    if after:
        compiled["after"] = _compile_user(user=after)

    if file:
        file_type = filetype(filename=file.discrim)

        compiled["file"] = {
            "size": round(os.path.getsize(f"{'static/uploads' if not file.deleted else 'archive'}/{file.discrim}") / 1024, 2),
            "type": file_type,
            "ext": filext(filename=file.discrim),
            "key": file.discrim,
            "created": file.created_at_friendly,
            "author": _compile_user(file.owner),
            "url": f"https://{root_url.lstrip('http://')}{'f' if file_type != 'image' else 'i'}/{file.discrim}" if not file.deleted else f"https://{root_url.lstrip('http://')}archive/{file.discrim}"
        }

    if url:
        compiled["url"] = {
            "link": url.url,
            "key": url.discrim,
            "created": url.created_at_friendly,
            "author": _compile_user(url.owner),
            "url": f"https://{root_url.lstrip('http://')}u/{url.discrim}"
        }

    return compiled