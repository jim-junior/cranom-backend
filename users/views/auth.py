from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import UserSerializer
from ..models import UserProfile
from rest_framework import permissions
import random
import string
from users.utils.ws_auth import encrypt


class GetWebSocketToken(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        # check if a UserProfile object with user as user exists
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        # Get Token from encrypt function
        token = encrypt(user_profile)

        return Response({"token": token}, status=status.HTTP_200_OK)
