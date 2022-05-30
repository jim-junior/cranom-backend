from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import UserSerializer


class CreateUser(APIView):

    def post(self, request: Request):
        print(request.data)
        data = request.data
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(data)
            return Response(data=request.data, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignInWithGithub(APIView):

    def post(self, request: Request):
        username = request.data['username']
        email = request.data['email']
        if self.checkIfUsernameExists(username):
            user = User.objects.get(username=username)
            # Sign in user and return jwt token
            tokens = self.get_tokens_for_user(user)
            return Response(data=tokens, status=status.HTTP_200_OK)

        else:
            user = User.objects.create_user(username=username, email=email)
            # Sign in user and return jwt token
            tokens = self.get_tokens_for_user(user)
            return Response(data=tokens, status=status.HTTP_200_OK)

    def checkIfUsernameExists(self, username):
        try:
            User.objects.get(username=username)
            return True
        except User.DoesNotExist:
            return False

    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
