import os
import django
from django.core.management import call_command

# Set your Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AcademiX.settings")
django.setup()

with open("full_data.json", "w", encoding="utf-8") as f:
    call_command("dumpdata", indent=4, stdout=f)
