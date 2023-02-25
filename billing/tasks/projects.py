from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from billing.models import Card, Transaction
from deployments.models import Project, Node
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
        per_hour = 0
    elif plan == "micro":
        per_hour = 15 / 720
    elif plan == "standard":
        per_hour = 35 / 720
    elif plan == "medium":
        per_hour = 75 / 720
    elif plan == "large":
        per_hour = 150 / 720

    # get hours in seconds provided
    hours = seconds / 3600
    return hours * per_hour


@shared_task
def __charge_projects():
    for project in Project.objects.all():
        if project.deployed:
            last_charged = project.last_charged
            # if last_charged date s more that a month ago
            if last_charged <= datetime.datetime.now() - datetime.timedelta(days=30):
                # get seconds since last charged
                seconds = (datetime.datetime.now() -
                           last_charged).total_seconds()
                # get amount to charge
                amount = get_project_amount(project.plan, seconds)
                # get User profile
                user_profile = UserProfile.objects.get(user=project.user)
                # check if user has any cards
                if user_profile.card_set.all().count() > 0:
                    # get first card
                    card = user_profile.card_set.all()[0]
                    if card.card_token:

                        tx = Transaction(
                            user=user_profile,
                            amount=amount,
                            card=card,
                            project=project,
                            reason="Monthly charge for project {}".format(
                                project.name),
                            tx_type="project_charge"
                        )
                        tx.save()
                        # charge card
                        resp = charge_card_token(
                            card.card_token,
                            str(tx.trans_id),
                            amount,
                            email=user_profile.email,
                        )
                    else:
                        print("No card token")
                else:
                    print("No cards")


@shared_task
def charge_projects():
    for project in Project.objects.all():
        amount = 0
        user_profile = UserProfile.objects.get(user=project.user)
        for node in project.node_set.all():
            pass
