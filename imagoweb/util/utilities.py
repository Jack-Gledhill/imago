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
from PIL import Image

# =========================
# Import local dependencies
# =========================
from imagoweb.util.blueprints import user
from imagoweb.util.constants import cache, config, const, pool

def get_user(token_or_id: Union[str, int]) -> Union[user, None]:
    """Retrieves a user with a given API token or user ID.
    
    The token is used for backend user retrieval but also for authentication when uploading images."""

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
    while discrim in [image.discrim for image in cache.images]:
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

def allowed_file(filename: str):
    """This checks to see if the extension of the provided filename is legal according to the configuration file."""
    
    return "." in filename and filename.rsplit(".", 1)[1].lower() in config.allowed_extensions

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

def optimise_image(file: Any,
                   discriminator: str):
    """Takes in an image object from Flask and optimises it according to the configuration.
    
    Because the default .save function doesn't allow for optimisation kwargs, we need to save the image, 
    open it with PIL and overwrite the image with the optimised data."""

    path = f"static/uploads/{discriminator}"

    file.save(path)
    saved_image = Image.open(path)

    saved_image.save(fp=path,
                     optimize=config.file_optimisation.compress,
                     quality=config.file_optimisation.quality)