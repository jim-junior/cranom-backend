from channels.layers import get_channel_layer
from users.models import UserProfile, Notification
from users.serializers import NotificationSerializer


def create_notification(user: UserProfile, message: str, link: str = None, notification_type: str = "info", link_text: str = None):
    """
    Creates a notification for a user
    """
    notification = Notification.objects.create(
        user=user,
        message=message,
        link=link,
        notification_type=notification_type,
        link_text=link_text,
    )
    notification.save()
    serializer = NotificationSerializer(notification)
    channel_layer = get_channel_layer()
    channel_layer.group_send(
        f"user_{user.user}", {
            "type": "user.notification",
            "message": "new_notification",
            "notification": serializer.data
        }
    )
