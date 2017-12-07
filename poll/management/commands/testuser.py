from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth.models import User
from django.core.management import CommandError


class Command(createsuperuser.Command):
    help = 'Create a superuser, and allow password to be provided'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--password', dest='password', default=None,
            help='Specifies the password for the superuser.',
        )

    def handle(self, *args, **options):
        password = options.get('password')
        username = options.get('username')
        email = options.get('email')

        if password and not username:
            raise CommandError("--username is required if specifying --password")

        if password and not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
