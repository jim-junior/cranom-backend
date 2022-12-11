from django.db import models
import uuid
from users.models import UserProfile
from deployments.models import Project

# Create your models here.


class Card(models.Model):
    card_number = models.CharField(max_length=16)
    expiration_date = models.CharField(max_length=5, blank=True)
    card_token = models.CharField(max_length=100, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    automatic = models.BooleanField(default=False)

    def __str__(self):
        return self.card_holder

    def __str__(self):
        return self.card_holder

    def __str__(self):
        return self.card_holder


class MMPhoneNumber(models.Model):
    phone_number = models.CharField(max_length=16)
    verification_code = models.CharField(max_length=6, blank=True)
    verified = models.BooleanField(default=False)
    country = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.phone_number

    def __str__(self):
        return self.phone_number

    def __str__(self):
        return self.phone_number


class Transaction(models.Model):
    trans_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    amount = models.FloatField()
    card = models.ForeignKey(Card, on_delete=models.CASCADE, blank=True)
    mm_phone_number = models.ForeignKey(
        MMPhoneNumber, on_delete=models.CASCADE, blank=True)
    transaction_status = models.CharField(max_length=100, default='pending')
    date_created = models.DateTimeField(auto_now_add=True)
    order_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    tx_type = models.CharField(max_length=50, null=True)
    reason = models.CharField(max_length=50)
    verification_url = models.CharField(max_length=300, blank=True)
    project = models.ForeignKey(
        Project, blank=True, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.transaction_id

    def __str__(self):
        return self.transaction_id

    def __str__(self):
        return self.transaction_id
