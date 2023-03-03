"""Install application."""
import os
import django
from .tools import *


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lnpayroll.settings")
    django.setup()
    migrate()
    load_fixtures()
    collect_static()
    create_user()
