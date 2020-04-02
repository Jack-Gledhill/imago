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