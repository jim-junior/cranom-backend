from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from users.models import UserProfile
from intergrations.models import GithubInstallation
from django.conf import settings
from rest_framework import serializers

# A serializer for Github installations


class GithubInstallationSerializer(serializers.ModelSerializer):

    class Meta:
        model = GithubInstallation
        fields = "__all__"

# An APIView that lists all Github installations for a user


class GithubInstallationList(generics.ListAPIView):
    """
    An API endpoint that lists all Github installations for a user
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Get User Profile
        user_profile = UserProfile.objects.get(user=self.request.user)
        return GithubInstallation.objects.filter(account=user_profile)

    def list(self, request):
        """
        Lists all Github installations for a user
        """
        queryset = self.get_queryset()
        serializer = GithubInstallationSerializer(queryset, many=True)
        return Response(serializer.data)


# Check if user has a github installation
class CheckGithubInstallation(APIView):
    """
    An API endpoint that checks if a user has a github installation
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        """
        Checks if a user has a github installation
        """
        user_profile = UserProfile.objects.get(user=request.user)
        if GithubInstallation.objects.filter(account=user_profile).exists():
            return Response(
                data={
                    "exists": True
                },
                status=status.HTTP_200_OK
            )
        return Response(
            data={
                "exists": False
            },
            status=status.HTTP_200_OK
        )
