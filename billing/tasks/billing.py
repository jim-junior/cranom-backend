from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from billing.models import Billing
from deployments.models import Node
from users.models import UserProfile
from .projects import get_project_amount
import datetime
from datetime import timedelta


@shared_task
def create_billing_task():
    # check of today is the first day of the month
    today = datetime.datetime.now()
    if today.day == 1:
        # get all users
        users = UserProfile.objects.all()
        for user in users:
            total_amount = 0
            nodes = Node.objects.filter(project__user=user)
            for node in nodes:
                last_turned_on = node.started_on
                if last_turned_on is None:
                    continue
                # Get the current time
                now = datetime.datetime.now()
                # Get the difference between the two
                diff = now - last_turned_on

                accumlated = get_project_amount(
                    node.plan, diff.total_seconds())
                bill_accumulated = 0
                if node.bill_accumulated is not None:
                    bill_accumulated = node.bill_accumulated
                amount = accumlated + bill_accumulated
                total_amount += amount
                node.bill_accumulated = 0
                node.started_on = now
                node.save()
            # Create a billing object
            billing = Billing.objects.create(
                user=user,
                amount=total_amount
            )
