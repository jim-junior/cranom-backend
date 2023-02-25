from users.models import Notification
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Deployment, Project


@receiver(post_save, sender=Deployment)
def send_deployment_notification(sender, instance, created, **kwargs):
    if created:
        project: Project = instance.project
        Notification.objects.create(
            user=project.user,
            message=f"Project <b>{project.name}</b> has been deployed successfully.",
            project_uuid=project.project_uuid,
            link=f'/projects/p/{project.project_uuid}',
            link_text='View Project',
            title='Project Deployed'
        )
