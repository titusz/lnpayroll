"""Initialize a fresh installation (resets pre-existing development database)."""
import os
import django
from .tools import *


if __name__ == "__main__":
    # DB deletion must happen before connecting
    delete_dev_db()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lnpayroll.settings")
    django.setup()
    migrate()
    load_fixtures()
    collect_static()
    create_user()
