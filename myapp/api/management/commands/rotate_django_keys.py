"""
Django management command to rotate the SECRET_KEY in the project's root .env file.

Usage:
    python manage.py rotate_django_keys
    python manage.py rotate_django_keys --env-file /custom/path/.env
    python manage.py rotate_django_keys --no-backup
"""

import re
import secrets
import string
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


def generate_secret_key(length: int = 50) -> str:
    """Generate a Django-style secret key using the standard character set."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return "".join(secrets.choice(chars) for _ in range(length))


def mask(key: str) -> str:
    """Show only the first 6 characters; mask the rest."""
    return key[:6] + "*" * (len(key) - 6) if len(key) > 6 else "***"


class Command(BaseCommand):
    help = "Rotate the Django SECRET_KEY in the project root .env file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--env-file",
            default=None,
            help=(
                "Path to the .env file. "
                "Defaults to BASE_DIR/.env (the hkn-portal repo root)."
            ),
        )
        parser.add_argument(
            "--no-backup",
            action="store_true",
            default=False,
            help="Skip creating a timestamped backup of the current .env file.",
        )

    def handle(self, *args, **options):
        # Resolve .env path
        if options["env_file"]:
            env_path = Path(options["env_file"]).resolve()
        else:
            # settings.BASE_DIR points to the repo root (where manage.py lives)
            env_path = Path(settings.BASE_DIR) / ".env"

        if not env_path.exists():
            raise CommandError(
                f".env file not found at {env_path}\n"
                "Use --env-file to specify a custom path."
            )

        original = env_path.read_text()

        # Match:  DJANGO_SECRET_KEY = 'value'  /  DJANGO_SECRET_KEY="value"  /  DJANGO_SECRET_KEY=value
        pattern = re.compile(
            r"^(DJANGO_SECRET_KEY\s*=\s*)(['\"]?)(.+?)(\2)\s*$",
            re.MULTILINE,
        )

        match = pattern.search(original)
        if not match:
            raise CommandError(
                "No SECRET_KEY entry found in .env.\n"
                "Expected a line like:  SECRET_KEY=your-current-key"
            )

        old_key = match.group(3)
        new_key = generate_secret_key()
        quote = match.group(2)  # preserve original quoting style
        replacement = f"{match.group(1)}{quote}{new_key}{quote}"
        updated = pattern.sub(replacement, original, count=1)

        # Optional backup
        if not options["no_backup"]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = env_path.parent / f".env.bak.{timestamp}"
            backup_path.write_text(original)
            self.stdout.write(f"  Backup saved → {backup_path}")

        env_path.write_text(updated)

        self.stdout.write(f"  OLD SECRET_KEY : {mask(old_key)}")
        self.stdout.write(f"  NEW SECRET_KEY : {mask(new_key)}")
        self.stdout.write(
            self.style.SUCCESS(f"✓ SECRET_KEY successfully rotated in {env_path}")
        )
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("Next steps:"))
        self.stdout.write(
            "  1. Restart the Django server so it picks up the new key.\n"
            "     Local :  Ctrl-C  then  python manage.py runserver\n"
            "     Server:  sudo service apache2 restart"
        )
        self.stdout.write(
            "  2. All active sessions will be invalidated — "
            "users will need to log in again."
        )
        self.stdout.write(
            "  3. Password-reset links and CSRF tokens signed with "
            "the old key will stop working."
        )