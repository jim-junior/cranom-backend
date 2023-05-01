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
from ..utils.user_utils import encrypt, decrypt
import time
from django.core.mail import send_mail
from ..utils.kube_utils.kube_user import create_namespace, create_docker_pull_secret

restricted_names = [
    "admin",
    "default",
    "kube-system",
    "kube-proxy",
    "kube-public",
    "kpack",
    "kube-node-lease",
    "ingress",
    "external-dns",
    "cranom",
    "prometheus",
    "grafana",
    "cert-manager",
    "cert-manager-cainjector",
    "cert-manager-webhook",
    "cert-manager-controller",
    "kubernetes-dashboard",
    "kubernetes-dashboard-metrics-scraper",
    "government",
    "government-internal",
    "government-external",
]


def sendActivationEmail(userprofile):
    user_token = encrypt(userprofile.username, userprofile.email)
    print(user_token)
    # send email to user with the token
    send_mail(
        "Activate your account",
        "Visit the link to activate your account: http://localhost:8000/activate/" + user_token,
        '"Cranom INC" <system@cranom.ml>',
        [userprofile.email],
        fail_silently=True,
        html_message="""<!DOCTYPE html><html lang="en"><head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Verifiy Your Email</title>
            </head>
            <body>
                <style>
                    .verify {
                        padding: 20px;
                        background-color: #006eff;
                        color: #fff;
                        border-radius: 10px;
                    }
                </style>
                <h1 style="padding: 20px;">Verifiy Your Email</h1>
                <p style="padding: 20px;">Click The button below inorder to verifiy your email and activate your account</p>
                <a class="verify" style="padding: 20px;background-color: #006eff;color: #fff;" href="http://cranom.ml/activate/"""+user_token + """\">Verify your Account</a>
            </body>
            </html>"""
    )


# An APIView that resends the activation email
class ResendActivationEmail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        user = request.user
        profile = UserProfile.objects.get(user=user)
        sendActivationEmail(profile)
        return Response(status=status.HTTP_200_OK)


class CreateUser(APIView):

    def post(self, request: Request):
        data = request.data
        username = data["username"]
        email = data["email"]
        password = data["password"]
        # check if user with the same email or username exists

        if User.objects.filter(username=username).exists() or username in restricted_names:
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

        sendActivationEmail(userprofile)
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
        gh_id = request.data['gh_id']
        avatar = request.data['picture']
        if self.checkIfEmailExists(gh_id):
            profile = UserProfile.objects.get(gh_id=gh_id)
            user = profile.user
            # Sign in user and return jwt token
            tokens = self.get_tokens_for_user(user)
            return Response(data=tokens, status=status.HTTP_200_OK)

        else:
            # create a random username that is not in use
            username = ''.join(random.choices(string.ascii_lowercase, k=10))
            while User.objects.filter(username=username).exists() or username in restricted_names:
                username = ''.join(random.choices(
                    string.ascii_lowercase, k=10))
            user = User.objects.create_user(username=username, email=email)
            userprofile = UserProfile.objects.create(
                user=user,
                is_active=False,
                email=email,
                username=username,
                gh_id=gh_id,
                avatar=avatar
            )
            userprofile.save()
            sendActivationEmail(userprofile)
            # Sign in user and return jwt token
            tokens = self.get_tokens_for_user(user)
            return Response(data=tokens, status=status.HTTP_200_OK)

    def checkIfEmailExists(self, gh_id):
        try:
            UserProfile.objects.get(gh_id=gh_id)
            return True
        except UserProfile.DoesNotExist:
            return False

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class LinkGithubAccount(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        profile = UserProfile.objects.get(user=request.user)
        if profile.gh_id:
            return Response({"message": "Github account already linked"}, status=status.HTTP_400_BAD_REQUEST)
        gh_id = request.data['gh_id']
        avatar = request.data['picture']
        profile.gh_id = gh_id
        profile.avatar = avatar
        profile.save()
        return Response(status=status.HTTP_200_OK)


class ActivateAccount(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)
        data = request.data
        token = data['token']
        if userprofile.is_active:
            return Response({"message": "Account already activated"}, status=status.HTTP_400_BAD_REQUEST)
        decrypted_obj = decrypt(token)
        if decrypted_obj['email'] != userprofile.email or decrypted_obj['username'] != userprofile.username:
            return Response({"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        created_at = decrypted_obj['time']
        # Check if the token has spent more that 24 hours
        if (created_at + 24 * 60 * 60) < time.time():
            return Response({"message": "Token has expired"}, status=status.HTTP_400_BAD_REQUEST)
        userprofile.is_active = True
        userprofile.save()
        # create kube namespace for the user
        """ create_namespace(userprofile)
        create_docker_pull_secret(userprofile) """
        return Response({"message": "Account activated"}, status=status.HTTP_200_OK)


class ChangePassword(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)
        data = request.data
        old_password = data['old_password']
        new_password = data['new_password']
        if not user.check_password(old_password):
            return Response({"message": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed"}, status=status.HTTP_200_OK)


# An API View that deletes a user account. It requires the request to have a request header named X-Password-Token with the password:
# X-Password-Token: password
class DeleteUser(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)
        data = request.data
        password = data['password']
        if not user.check_password(password):
            return Response({"message": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response({"message": "User deleted"}, status=status.HTTP_200_OK)


# An APIiew that checks if user is verified
class IsVerified(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request):
        user = request.user
        userprofile = UserProfile.objects.get(user=user)
        return Response({"verified": userprofile.is_active}, status=status.HTTP_200_OK)
