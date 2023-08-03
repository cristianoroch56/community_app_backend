from firebase_admin.messaging import Message, Notification
from notification.models import SendNotification
from fcm_django.models import FCMDevice
from helper.slack_logger import send_error_to_slack as logs
import json


def send_notification(user_id, title, content):
    try:
        device = FCMDevice.objects.filter(user=user_id).first()
        if not device:
            pass
        result = device.send_message(
            Message(notification=Notification(title=title, body=content))
        )
        if result["success"]:
            logs(json.dumps("Notification sent successfully"))
            return True
        else:
            logs(json.dumps("Notification sending failed"))
            return False
    except Exception as e:
        logs(json.dumps(str(e)))
        return False


def create_notification(user, title, content, content_id):
    # create notification
    user_notify = SendNotification.objects.create(
        user=user, title=title, content=content, content_id=content_id
    )
    try:
        # Get the related UserProfile object using the related manager
        user_profile = user.user_profile.get()
        # Check if the user's UserProfile has push_notification enabled before sending the notification
        if user_profile.push_notification:
            send_notification(user_id=user.id, title=title, content=content)
    except:
        # Handle the situation where user.user_profile is None
        pass

    return user_notify
