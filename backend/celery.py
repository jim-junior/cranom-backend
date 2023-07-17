import os

from celery import Celery
from dotenv import load_dotenv
load_dotenv()

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

CELERY_REDIS_URL = os.getenv("CELERY_BROKER_REDIS_URL")
print(CELERY_REDIS_URL)

app = Celery(
    'backend', broker=CELERY_REDIS_URL)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
