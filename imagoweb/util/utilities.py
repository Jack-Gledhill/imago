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

# ------------------------
# Third-party dependencies
# ------------------------
from requests import post
from PIL import Image

# =========================
# Import local dependencies
# =========================
from imagoweb.util.blueprints import user
from imagoweb.util.constants import cache, config, const, pool

WEBHOOK_URL = "https://discordapp.com/api/webhooks/{id}/{token}"

DISCORD_LOG_FORMATS = {
    "FILE_DELETE": ":wastebasket: {user} deleted a file:\n{url}?token={hook_token}",
    "FILE_UPLOAD": ":inbox_tray: {user} uploaded a file:\n{url}",
    "FILE_RESTORE": ":link: {admin} restored a file by {user}:\n{url}",

    "USER_EDIT": ":pencil: {user} edited their account.",
    "USER_TOKEN_RESET": ":closed_lock_with_key: {user} reset their account token.",

    "FORCE_USER_CREATE": ":inbox_tray: {admin} created an account with the name {user}.",
    "FORCE_USER_EDIT": ":pencil: {user} was edited by {admin}.",
    "FORCE_USER_DELETE": ":wastebasket: {user} was deleted by {admin}.",
    "FORCE_USER_TOKEN_RESET": ":closed_lock_with_key: {user} had their token reset by {admin}.",
    "FORCE_FILE_DELETE": ":wastebasket: {admin} deleted a file by {user}:\n{url}?token={hook_token}",

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

def generate_discrim():
    """This generates a unique, available discriminator for an uploaded file."""

    # ====================
    # Generate the discrim
    # ====================
    discrim = "".join(choice(ascii_letters + digits) for i in range(config.generator.filename))

    # ====================================
    # Check to see if discrim is available
    # ====================================
    while discrim in [file.discrim for file in cache.files]:
        discrim = "".join(choice(ascii_letters + digits) for i in range(config.generator.filename))
        
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

def filetype(filename: str):
    """This checks to see if the extension of the provided filename is legal according to the configuration file.
    
    If allowed, the extension type (e.g: image/audio) is returned. Otherwise False is returned."""

    return config.allowed_extensions.get("." in filename and filename.rsplit(".", 1)[1].lower(), False)

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

def make_discord_log(event: str,
                     **event_values: dict):
    """This sends a specific event log to Discord with the provided values.
    
    If Discord returns a 401, we internally disable Discord logging and warn the user that the token is invalid."""

    if config.discord.enabled:
        fmt = DISCORD_LOG_FORMATS.get(event)

        if fmt is None:
            return

        webhook = first(iterable=config.discord.webhooks,
                        condition=lambda hookconfig: event in hookconfig.events)

        if webhook is None:
            return

        message = fmt.format(hook_token=webhook.token,
                             **event_values)

        response = post(url=WEBHOOK_URL.format(id=webhook.id,
                                               token=webhook.token),
                        json={
                            "content": message,
                            "username": webhook.username
                        })

        # ==========================================================
        # Remove from config internally because the URL is incorrect
        # ==========================================================
        if response.status_code == 401:
            config.discord.webhooks.remove(webhook)

        return response