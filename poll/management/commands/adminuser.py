from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth.models import User
from django.core.management import CommandError


class Command(createsuperuser.Command):

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')

        if not username:
            raise CommandError("--username is required")

        if not User.objects.filter(username=username).exists():
            password = User.objects.make_random_password()
            User.objects.create_superuser(username=username, email=email, password=password)
            print("*" * 20)
            print("ADMIN CREATED WITH PASSWORD: %s" % password)
            print("*" * 20)
        else:
            print("*" * 20)
            print("ADMIN ACCOUNT ALREADY EXISTS")
            print("*" * 20)
