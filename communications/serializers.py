from .models import NewsLetter
from rest_framework import serializers


class NewsLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsLetter
        fields = ('email', 'date_added')
