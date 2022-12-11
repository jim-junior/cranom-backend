from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import UserSerializer, NotificationSerializer
from users.models import UserProfile, Notification
from rest_framework import permissions


class GetUnreadNotifications(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request, *args, **kwargs):
        user = request.user
        # get user profile
        user_profile = UserProfile.objects.get(user=user)
        notifications = Notification.objects.filter(
            user=user_profile, is_read=False)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarkNotificationAsRead(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request, *args, **kwargs):
        user = request.user
        # get user profile
        user_profile = UserProfile.objects.get(user=user)
        notification_id = request.data.get('notification_id')
        notification = Notification.objects.get(
            id=notification_id, user=user_profile)
        notification.is_read = True
        notification.save()
        return Response(status=status.HTTP_200_OK)


class MarkAllNotificationsAsRead(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request, *args, **kwargs):
        user = request.user
        # get user profile
        user_profile = UserProfile.objects.get(user=user)
        notifications = Notification.objects.filter(
            user=user_profile, is_read=False)
        for notification in notifications:
            notification.is_read = True
            notification.save()
        return Response(status=status.HTTP_200_OK)
