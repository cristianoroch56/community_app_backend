from rest_framework import serializers
from userprofile.models import UserProfile
from django.db import IntegrityError
from django.utils.translation import gettext as _


class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    mobile_number = serializers.CharField(
        source="user.username", read_only=True, required=False
    )

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "mobile_number",
            "profile_pic",
            "relation_with_main_member",
            "birthdate",
            "education",
            "marital_status",
            "currently_living_at",
            "created_at",
            "updated_at",
            "push_notification",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate(self, attrs):
        # Retrieve the 'mobile_number' from the request data
        mobile_number = self.context.get("extra").get("mobile_number")

        # Check if the 'mobile_number' already exists in the database
        if UserProfile.objects.filter(user__username=mobile_number).exists():
            raise serializers.ValidationError(
                {"mobile_number": [_("Mobile number already exists.")]}
            )

        return attrs

    def update(self, instance, validated_data):
        extra = self.context.get("extra")
        # Handle 'first_name' and 'last_name' separately
        # Retrieve 'first_name' and 'last_name' from the request data
        first_name = extra.get("first_name")
        last_name = extra.get("last_name")
        mobile_number = extra.get("mobile_number")
        instance.user.first_name = first_name
        instance.user.last_name = last_name
        instance.user.username = mobile_number
        instance.user.save()

        return super().update(instance, validated_data)
