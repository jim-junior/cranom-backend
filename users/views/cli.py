import time
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import UserSerializer
from ..models import UserProfile, AuthTokens
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from ..utils.user_utils import get_cli_token, decode_cli_token


class GetCLIToken(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        username = user.username
        token = get_cli_token(username, "year", "cli")
        return Response(data={"token": token}, status=status.HTTP_201_CREATED)


class LoginWithCli(APIView):

    def post(self, request):

        data = request.data
        token = data["token"]
        username = data["username"]
        platform = data["platform"]
        token_data = decode_cli_token(token)
        if token_data == "Failed":
            return Response(data={"message": "Invalid Token"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        exp = token_data["exp"]
        t_username = token_data["username"]
        if User.objects.filter(username=username).exists() == False:
            return Response(data={"message": "The user input does not exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if t_username != username:
            return Response(data={"message": "Token Belongs to another user. Using another users Token might lead to account bans"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if exp <= time.time():
            return Response(data={"message": "Token is Expired"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        user = User.objects.get(username=username)
        token = Token.objects.create(user=user)
        autht = AuthTokens.objects.create(
            user=user, token=token, platform=platform)

        authdata = {
            "id": user.id,
            'token': token.key,
        }
        return Response(data=authdata, status=status.HTTP_200_OK)
