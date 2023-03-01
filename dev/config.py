"""Initialize a fresh installation (resets pre-existing development database).
- creates the database
- import theme fixtures
- create initial user
"""
import shutil
import sys
import os
from loguru import logger as log

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lnpayroll.settings")
from django.contrib.auth import get_user_model
from django.core import management
import django
import pathlib


HERE = pathlib.Path(__file__).parent.absolute()
django.setup()


def delete_dev_db():
    dev_db = HERE / "dev.db"
    if dev_db.exists():
        do_delete = input(f"Delete dev database at {dev_db} (y/n)?: ")
        if do_delete != "y":
            log.info("Leaving DB as is.")
            return
        try:
            os.remove(dev_db)
            log.info(f"Deleted dev database at {dev_db}?")
        except Exception as e:
            log.error(f"{e}\nFailed deleting dev database\nRetry after stopping dev server!")
            sys.exit(0)


def reset_migrations():
    mig_path = HERE.parent / "lnpayroll/migrations"
    do_delete = input(f"Reset migrations at {mig_path} (y/n)?: ")
    if do_delete != "y":
        log.info("Leaving migrations as is.")
        return
    try:
        shutil.rmtree(mig_path)
        log.info("Migrations deleteted")
    except Exception as e:
        log.error(f"{e}\nFailed deleting migrations\nAborting!")
        sys.exit(0)
    management.call_command("makemigrations", "lnpayroll")


def migrate():
    log.info("Run database migrations")
    management.call_command("migrate")


def load_fixtures():
    log.info("Load theme fixture")
    management.call_command("loaddata", "--app", "admin_interface.Theme", "theme")


def create_user():
    from django.conf import settings
    import secrets

    log.info("Create initial user")
    if settings.DEBUG:
        username = "demo"
        password = "demo"
        email = "demo@example.com"
    else:
        username = "admin"
        password = secrets.token_hex(32)
        email = settings.SITE_EMAIL

    User = get_user_model()

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, password=password, email=email)
        log.info("############ CREATED INITIAL SUPERUSER ############ ")
        log.info(f"Username: {username}")
        log.info(f"Password: {password}")
    else:
        log.info("Skipped creating initial user - already exists")


def config():
    delete_dev_db()
    reset_migrations()
    migrate()
    load_fixtures()
    create_user()


if __name__ == "__main__":
    config()
