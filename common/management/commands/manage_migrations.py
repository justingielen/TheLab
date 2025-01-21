from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import connection
from django.apps import apps
from pathlib import Path
import os
import shutil
from datetime import datetime


class Command(BaseCommand):
    help = "Manages migrations in a safe and environment-agnostic way."

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help="Reset migrations by clearing files and history (use with caution)."
        )
        parser.add_argument(
            '--backup',
            action='store_true',
            help="Backup existing migration files before any reset or modification."
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write("Starting migration management...")
            
            if options['backup']:
                backup_path = self._create_backup()
                self.stdout.write(
                    self.style.SUCCESS(f"Backup completed. Files saved to: {backup_path}")
                )
            
            if options['reset']:
                self.stdout.write("Resetting migrations...")

                self._clean_migration_files()
                self._reset_migration_history()
                self._create_fresh_migrations()

                self.stdout.write(self.style.SUCCESS("Migrations reset successfully."))
            else:
                self._apply_unapplied_migrations()
                self.stdout.write(self.style.SUCCESS("Migrations applied successfully."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            raise CommandError(f"Migration management failed: {e}")

    def _create_backup(self):
        """Creates a timestamped backup of migration files."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f'migrations_backup_{timestamp}'
        os.makedirs(backup_dir, exist_ok=True)

        for app in apps.get_app_configs():
            migrations_dir = Path(app.path) / "migrations"
            if migrations_dir.exists():
                app_backup_dir = Path(backup_dir) / app.label
                shutil.copytree(migrations_dir, app_backup_dir, dirs_exist_ok=True)
                self.stdout.write(f"Backed up migrations for {app.label}.")

        return backup_dir

    def _clean_migration_files(self):
        """Deletes all migration files except __init__.py for all apps."""
        for app in apps.get_app_configs():
            migrations_dir = Path(app.path) / "migrations"
            if migrations_dir.exists():
                for file in migrations_dir.glob("*.py"):
                    if file.name != "__init__.py":
                        file.unlink()
                        self.stdout.write(f"Deleted {file} in {app.label} migrations.")
    
    def _reset_migration_history(self):
        """Resets migration history in the database."""
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM django_migrations")
        self.stdout.write("Cleared migration history in the database.")

    def _create_fresh_migrations(self):
        """Generates fresh migration files for all apps."""
        call_command("makemigrations", verbosity=1)

    def _apply_unapplied_migrations(self):
        """Applies any unapplied migrations."""
        call_command("migrate", verbosity=1)