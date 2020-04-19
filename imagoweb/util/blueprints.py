# ========================
# Import PATH dependencies
# ========================
# ------------------------
# Third-party dependencies
# ------------------------
from custos import blueprint

class user(blueprint):
    def __init__(self,
                 **user_data: dict):
        self.username = user_data.pop("username")
        self.password = user_data.pop("password")
        self.display_name = user_data.pop("display_name")

        self.is_admin = user_data.pop("admin")
        self.api_token = user_data.pop("token")

        self.user_id = user_data.pop("id")
        self.created_at = user_data.pop("created_at")

class upload(blueprint):
    def __init__(self,
                 **upload_data: dict):
        self.file_id = upload_data.pop("id")
        self.discrim = upload_data.pop("discrim")
        self.deleted = upload_data.pop("deleted")

        self.owner_id = upload_data.pop("owner_id")
        self.created_at = upload_data.pop("created_at")

        self.created_at_friendly = self.created_at.strftime("%d/%m/%Y %H:%M")

        self.owner = upload_data.pop("owner")

class url(blueprint):
    def __init__(self,
                 **url_data: dict):
        self.url_id = url_data.pop("id")
        self.discrim = url_data.pop("discrim")
        self.url = url_data.pop("url")

        self.owner_id = url_data.pop("owner_id")
        self.created_at = url_data.pop("created_at")

        self.created_at_friendly = self.created_at.strftime("%d/%m/%Y %H:%M")

        self.owner = url_data.pop("owner")

class webhook(blueprint):
    def __init__(self,
                 **webhook_data: dict):
        self.hook_id = webhook_data.pop("id")
        self.token = webhook_data.pop("token")

        self.username = webhook_data.pop("username")
        self.events = webhook_data.pop("events")

        self.url = f"https://discordapp.com/api/webhooks/{self.hook_id}/{self.token}"

class sysmsg(blueprint):
    def __init__(self,
                 **message_data: dict):
        self.msg_id = message_data.pop("id")
        self.recipient_id = message_data.pop("recipient_id")

        self.content = message_data.pop("content")

        self.created_at = message_data.pop("created_at")
        self.created_at_friendly = self.created_at.strftime("%d/%m/%Y at %H:%M")

class metadata(blueprint):
    def __init__(self,
                 **meta_data: dict):
        self.title = meta_data.pop("title")
        self.description = meta_data.pop("description")
        self.theme_colour = meta_data.pop("theme_colour")

        self.url = meta_data.pop("url") 
        self.image = meta_data.pop("image")
        self.thumbnail = meta_data.pop("thumbnail")
        self.site_name = meta_data.pop("site_name")

    @property
    def as_tags(self) -> str:
        """Returns all of the stored meta data as HTML tags that can be put straight into a template."""

        return f"""<meta property="og:title" content="{self.title}">
                   <meta name="twitter:title" content="{self.title}">

                   <meta name="theme-color" content="#{self.theme_colour}">
                   
                   <link rel="canonical" href="{self.url}">
                   <meta property="og:url" content="{self.url}">
                   <meta name="twitter:url" content="{self.url}">
                   
                   <meta name="description" content="{self.description}">
                   <meta property="og:description" content="{self.description}">
                   <meta name="twitter:description" content="{self.description}">
                   
                   <meta property="og:image" content="{self.image}">
                   <meta name="twitter:image" content="{self.image}">
                   <meta property="og:thumbnail" content="{self.thumbnail}">
                   
                   <meta property="og:site_name" content="{self.site_name}">
                   <meta property="og:type" content="website">"""