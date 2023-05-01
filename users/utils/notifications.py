from channels.layers import get_channel_layer
from users.models import UserProfile, Notification
from users.serializers import NotificationSerializer
from asgiref.sync import async_to_sync


def create_notification(user: UserProfile, title: str, message: str, link: str = None, notification_type: str = "info", link_text: str = None):
    """
    Creates a notification for a user
    """
    notification = Notification.objects.create(
        user=user,
        message=message,
        link=link,
        notification_type=notification_type,
        link_text=link_text,
        title=title
    )
    notification.save()
    serializer = NotificationSerializer(notification)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{str(user.user.id)}", {
            "type": "user.notification",
            "message": title,
            "notification": serializer.data
        }
    )
