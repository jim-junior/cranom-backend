from django.http import QueryDict
from billing.models import Transaction
import datetime
from users.models import Notification


def process_payment(data: QueryDict):
    """Process payment webhook recieved

    :param data: Dictionary with payment data.
    """
    tx_data = data["data"]
    if tx_data["status"] == "successful":
        tx_ref = tx_data["tx_ref"]
        tx_obj = Transaction.objects.get(trans_id=tx_ref)
        tx_obj.status = "success"
        tx_obj.save()
        tx_type = tx_obj.tx_type
        if tx_type == "project_charge":
            project = tx_obj.project
            project.last_charged = datetime.datetime.now()
            project.save()
            notification = Notification(
                user=project.user,
                message=f"Your project {project.name} has been charged",
                project_uuid=project.project_uuid,
            )
            notification.save()
