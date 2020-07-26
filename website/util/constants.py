# Copyright (C) JackTEK 2018-2020
# -------------------------------

# =====================
# Import PATH libraries
# =====================
# -----------------
# Builtin libraries
# -----------------
from datetime import datetime

# ------------------------
# Third-party dependencies
# ------------------------
from attrdict import AttrDict
from custos import version
from mistune import create_markdown, escape, HTMLRenderer
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html
from yaml import safe_load

# ======================
# Import local libraries
# ======================
from util.blueprints import User


config = AttrDict(safe_load(open(file="config.yml")))

const = AttrDict(dict(boot_dt=datetime.utcnow(),
                      superuser=User(username=config.superuser.username,
                                     password=config.superuser.password,

                                     created_at=datetime.utcnow(),

                                     token=config.superuser.token,
                                     admin=True,
                                     id=0)))

cache = AttrDict({"users": [const.superuser],
                  "files": [],
                  "urls": []})

epoch = datetime(year=2000,
                 month=1,
                 day=1,
                 hour=0,
                 minute=0,
                 second=1)

version = version(major=4,
                  minor=2,
                  patch=1,
                  release="stable")

app = None
postgres = None


class HighlightRenderer(HTMLRenderer):
    def block_code(self, 
                   code: str, 
                   lang=None):
        if lang:
            lexer = get_lexer_by_name(lang, stripall=True)
            formatter = html.HtmlFormatter(linenos=True, 
                                           full=True,
                                           style=config.code_style)
            return highlight(code, lexer, formatter)

        return "<pre><code>" + escape(code) + "</code></pre>"

markdown = create_markdown(renderer=HighlightRenderer(),
                           plugins=["strikethrough", "footnotes", "table", "url"])