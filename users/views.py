from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import UserSerializer
from .models import UserProfile
from rest_framework import permissions


class CreateUser(APIView):

    def post(self, request: Request):
        data = request.data
        username = data["username"]
        email = data["email"]
        password = data["password"]
        user = User.objects.create_user(username, email, password)
        userprofile = UserProfile.objects.create(
            user=user,
            is_active=False,
            email=email,
            username=username
        )
        userprofile.save()

        serializedData = UserSerializer(userprofile)
        return Response(data=serializedData.data, status=status.HTTP_201_CREATED)


class GetUserProfile(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        profile = UserProfile.objects.get(user=user)
        serializer = UserSerializer(profile)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


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
