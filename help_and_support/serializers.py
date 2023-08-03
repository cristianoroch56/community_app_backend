from rest_framework import serializers
from help_and_support.models import HelpAndSupport


class HelpAndSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpAndSupport
        fields = ["id", "user", "subject", "message", "status", "created_at"]
        read_only_fields = ["id", "created_at"]
