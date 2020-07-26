# Copyright (C) JackTEK 2018-2020
# -------------------------------

# ========================
# Import PATH dependencies
# ========================
# ------------
# Type imports
# ------------
from typing import Any, Callable, List, Iterable, Optional, Union
from util.blueprints import User


# -----------------
# Builtin libraries
# -----------------
from random import choice
from string import ascii_letters, digits

# ------------------------
# Third-party dependencies
# ------------------------
from flask import jsonify
from PIL import Image

# -------------------------
# Local extension libraries
# -------------------------
from util.constants import cache, config, const


def get_user(token_or_id: Union[str, int]) -> Union[User, None]:
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

    if (key == "api_token" and token_or_id == const.superuser.token) or \
       (key == "id" and token_or_id == const.superuser.id):
        return const.superuser

    return first(iterable=cache.users,
                 condition=lambda user: token_or_id in (user.token, user.id))

def check_user(token: Union[str, int, None]) -> Union[User, None]:
    """Runs checks to see if a user can be retrieved from a cookie."""

    if not token:
        return None

    return get_user(token_or_id=token)

def generate_key(cache_obj="files"):
    """This generates a unique, available key for an uploaded file."""

    key = "".join(choice(ascii_letters + digits) for i in range(config.generator.get(cache_obj)))

    while key in [item.key for item in getattr(cache, cache_obj)]:
        key = "".join(choice(ascii_letters + digits) for i in range(config.generator.get(cache_obj)))
        
    return key

def generate_token():
    """This simply generates a unique, available token for a user.
    
    There's no need to worry about the superuser token here because it will always have Master at the start of it and spaces can't be generated here."""

    token = "".join(choice(ascii_letters + digits) for i in range(config.generator.token))

    while token in [user.token for user in cache.users]:
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
                    user: User) -> bool:
    """Determines whether or not the provided user can and wants to bypass image compression."""

    cfg = config.file_optimisation.admin_bypass

    if False in (cfg.can_bypass, user.admin):
        return False

    if not header:
        return cfg.by_default

    return True

def optimise_image(key: str):
    """Takes in an file object from Flask and optimises it according to the configuration.
    
    Because the default .save function doesn't allow for optimisation kwargs, we need to save the file, 
    open it with PIL and overwrite the file with the optimised data."""

    path = f"static/uploads/{key}"
    saved_file = Image.open(path)

    saved_file.save(fp=path,
                    optimize=config.file_optimisation.compress,
                    quality=config.file_optimisation.quality)

def bytes_4_humans(count: int) -> str:
    """Returns a human friendly interpretation of bytes."""

    # Bytes
    if 1024 > count >= 1:
        return f"{round(count, 2)} B"

    # Kilobytes
    if 1024 > count / 1024 >= 1:
        return f"{round(count / 1024, 2)} KB"

    # Megabytes
    if 1024 > count / 1024 ** 2 >= 1:
        return f"{round(count / 1024 ** 2, 2)} MB"

    # Gigabytes
    if 1024 > count / 1024 ** 3 >= 1:
        return f"{round(count / 1024 ** 3, 2)} GB"

    # Terabytes
    if 1024 > count / 1024 ** 4 >= 1:
        return f"{round(count / 1024 ** 4, 2)} TB"

    # Return in Petabytes if all else fails
    return f"{round(count / 1024 ** 5, 2)} PB"

def respond(code: Optional[int] = 200,
            msg: Optional[str] = "OK",
            **extras: dict):
    """Responds with a JSON payload."""

    return jsonify(dict(code=code,
                        message=msg,
                        **extras)), code