from rest_framework import serializers
from .models import *


class CardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Card
        fields = "__all__"


class MMPhoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = MMPhoneNumber
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = "__all__"
