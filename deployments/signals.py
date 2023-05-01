from users.models import Notification
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.utils.notifications import create_notification
from .models import Deployment, Project


@receiver(post_save, sender=Deployment)
def send_deployment_notification(sender, instance, created, **kwargs):
    if created:
        project: Project = instance.project
        create_notification(
            project.user,
            'New Deployment',
            f"""A new Deployment for <b>{project.name}<b> has been deployed successfully.""",
            f'/projects/p/{project.project_uuid}',
            'success',
            'View Project'
        )
