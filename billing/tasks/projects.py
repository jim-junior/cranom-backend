from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from billing.models import Card, Transaction
from deployments.models import Node
from users.models import UserProfile
from billing.utils.charge import charge_card_token
import datetime


PROJECT_PLANS = (
    ("hobby", "hobby"),  # free
    ("micro", "micro"),  # $ 15 /month
    ("standard", "standard"),  # $ 35 /month
    ("medium", "medium"),  # $ 75 /month
    ("large", "large"),  # $ 150 /month
)


def get_project_amount(plan, seconds):
    per_hour = 0
    if plan == "hobby":
        per_hour = 5 / 720
    elif plan == "micro":
        per_hour = 15 / 720
    elif plan == "standard":
        per_hour = 35 / 720
    elif plan == "medium":
        per_hour = 75 / 720
    elif plan == "large":
        per_hour = 150 / 720

    # get hours in seconds provided
    hours = int(seconds / 3600)
    print("hours", hours)
    print("per_hour", per_hour)
    print("plan", plan)
    return hours * per_hour
