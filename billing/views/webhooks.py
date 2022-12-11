from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from billing.views.fw import process_payment


class FlutterwaveTransactionWebhooks(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request, *args, **kwargs):
        data = request.data
        print(data)
        if data["event"] == "charge.completed":
            process_payment(data)
        return Response(status=status.HTTP_200_OK)
