from django.core.management.base import BaseCommand, CommandError
from main_app.models import Bank

class Command(BaseCommand):
    help = "Create a bank client with an API key (stored plaintext here for simplicity)."

    def add_arguments(self, parser):
        parser.add_argument('--name', required=True, help='Bank name (unique)')
        parser.add_argument('--api-key', required=True, help='API key to store')

    def handle(self, *args, **options):
        name = options['name']
        api_key = options['api_key']

        if Bank.objects.filter(name=name).exists():
            raise CommandError(f"Bank with name '{name}' already exists.")
        if Bank.objects.filter(api_secret_key=api_key).exists():
            raise CommandError("This API key is already in use.")

        bank = Bank(name=name, api_secret_key=api_key, is_active=True)
        bank.save()
        self.stdout.write(self.style.SUCCESS(
            f"Created bank '{name}'. Use this x-api-key in requests:\n{api_key}"
        ))
