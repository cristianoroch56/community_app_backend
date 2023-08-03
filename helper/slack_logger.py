from django.conf import settings
import requests


def send_error_to_slack(data):
    webhook_url = settings.SLACK_WEBHOOK_URL
    payload = {"text": data}
    response = requests.post(webhook_url, json=payload)

    if response.status_code != 200:
        # Handle the case where the message couldn't be sent to Slack
        pass
