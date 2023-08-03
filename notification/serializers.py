from rest_framework import serializers
from notification.models import SendNotification


class SendNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendNotification
        fields = "__all__"
