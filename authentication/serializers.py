from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from authentication.models import ActivationOTP
from django.utils import timezone
from django.contrib.auth import get_user_model
from authentication.models import ForgetPasswordToken
from django.utils.translation import gettext as _


User = get_user_model()


# UserSerializer use for user creation
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer class for User model.
    """

    username = serializers.CharField(
        max_length=150, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "username", "password", "country_code","country_flag")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["is_active"] = False  # Set is_active to False
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class ActivationOTPSerializer(serializers.Serializer):
    username = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        username = data.get("username")
        otp = data.get("otp")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("User not found."))

        activation_otp = ActivationOTP.objects.filter(user=user, otp=otp).first()
        if not activation_otp:
            raise serializers.ValidationError(_("Invalid OTP."))

        # Check if the OTP has expired
        if activation_otp.expires_at < timezone.now():
            raise serializers.ValidationError(_("OTP has expired."))

        # Set the user's is_active status to True
        user.is_active = True
        user.save()

        return data


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("Invalid username or password."))

        if not user.check_password(password):
            raise serializers.ValidationError(_("Invalid username or password."))

        if not user.is_active:
            raise serializers.ValidationError(_("Verify OTP to active account"))

        attrs["user"] = user
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        token = self.context["request"].META.get("HTTP_AUTHORIZATION").split(" ")[1]

        if not username or not password:
            raise serializers.ValidationError(_("Provide username and password"))

        if not ForgetPasswordToken.objects.filter(
            user__username=username, token=token
        ).exists():
            raise serializers.ValidationError(_("Provide correct credentials"))

        return attrs
