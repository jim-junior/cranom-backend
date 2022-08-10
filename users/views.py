from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import UserSerializer
from .models import UserProfile
from rest_framework import permissions
import random
import string


class CreateUser(APIView):

    def post(self, request: Request):
        data = request.data
        username = data["username"]
        email = data["email"]
        password = data["password"]
        # check if user with the same email or username exists
        if User.objects.filter(username=username).exists():
            return Response({"message": "User with the same username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"message": "User with the same email already exists"}, status=status.HTTP_400_BAD_REQUEST)
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
        email = request.data['email']
        if self.checkIfEmailExists(email):
            user = User.objects.get(email=email)
            # Sign in user and return jwt token
            tokens = self.get_tokens_for_user(user)
            return Response(data=tokens, status=status.HTTP_200_OK)

        else:
            # create a random username that is not in use
            username = ''.join(random.choices(string.ascii_lowercase, k=10))
            while User.objects.filter(username=username).exists():
                username = ''.join(random.choices(
                    string.ascii_lowercase, k=10))
            user = User.objects.create_user(username=username, email=email)
            userprofile = UserProfile.objects.create(
                user=user,
                is_active=False,
                email=email,
                username=username
            )
            userprofile.save()
            # Sign in user and return jwt token
            tokens = self.get_tokens_for_user(user)
            return Response(data=tokens, status=status.HTTP_200_OK)

    def checkIfEmailExists(self, email):
        try:
            User.objects.get(email=email)
            return True
        except User.DoesNotExist:
            return False

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
