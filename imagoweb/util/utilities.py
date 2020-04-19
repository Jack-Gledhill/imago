# ========================
# Import PATH dependencies
# ========================
# -----------------
# Builtin libraries
# -----------------
import re

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
from imagoweb.util.blueprints import sysmsg, user
from imagoweb.util.constants import cache, config, const, pool

DISCORD_LOG_FORMATS = {
    "FILE_DELETE": ":wastebasket: {user} deleted a file:\n{url}?token={hook_token}",
    "FILE_UPLOAD": ":inbox_tray: {user} uploaded a file:\n{url}",
    "FILE_RESTORE": ":link: {admin} restored a file by {user}:\n{url}",

    "URL_SHORTEN": ":link: {user} shortened a URL at {url}:\n{link}",
    "URL_DELETE": ":wastebasket: {user} deleted a shortened URL:\n{link}",

    "USER_EDIT": ":pencil: {user} edited their account.",
    "USER_TOKEN_RESET": ":closed_lock_with_key: {user} reset their account token.",

    "FORCE_USER_CREATE": ":inbox_tray: {admin} created an account with the name {user}.",
    "FORCE_USER_EDIT": ":pencil: {user} was edited by {admin}.",
    "FORCE_USER_DELETE": ":wastebasket: {user} was deleted by {admin}.",
    "FORCE_USER_TOKEN_RESET": ":closed_lock_with_key: {user} had their token reset by {admin}.",
    "FORCE_FILE_DELETE": ":wastebasket: {admin} deleted a file by {user}:\n{url}?token={hook_token}",
    "FORCE_URL_DELETE": ":wastebasket: {admin} deleted a shortened URL by {user}:\n{link}",

    "ADMIN_TOGGLE_ON": ":lock: {admin} made {user} an Administrator.",
    "ADMIN_TOGGLE_OFF": ":unlock: {admin} removed Administrator from {user}."
}

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
    
    If allowed, the extension type (e.g: image/audio) is returned. Otherwise False is returned."""

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

def dispatch_event(event: str,
                   recipient_id: int,
                   **hook_data: dict):
    """Dispatches a particular event.
    
    This creates a log at the DEBUG level as well as triggering any applicable system messages and webhook logs."""

    console.debug(text=f"Event {event} was triggered for user {recipient_id}.")

    if event in config.sys_messaging.events:
        create_sys_msg(content=config.sys_messaging.events.get(event),
                       recipient_id=recipient_id)

    make_discord_log(event=event,
                     **hook_data)

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
        fmt = DISCORD_LOG_FORMATS.get(event)

        if fmt is None:
            return

        webhook = first(iterable=const.webhooks,
                        condition=lambda hookconfig: event in hookconfig.events)

        if webhook is None:
            return

        message = fmt.format(hook_token=webhook.token,
                             **event_values)

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