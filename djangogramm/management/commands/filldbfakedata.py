from django.core.management.base import BaseCommand, CommandError
from djangogramm import fake_fill_db


class Command(BaseCommand):
    help = "Fills data base with fake data."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting fill db..."))
        fill_db_bool = fake_fill_db.main()
        if not fill_db_bool:
            raise CommandError("Something went wrong with db fills!")
        self.stdout.write(self.style.SUCCESS("Db filled successfully!"))
