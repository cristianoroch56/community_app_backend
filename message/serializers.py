from rest_framework import serializers
from authentication.models import User
from message.models import Thread, ChatMessage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name")


class ThreadSerializer(serializers.ModelSerializer):
    user1 = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user2 = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user1_data = UserSerializer(read_only=True, source="user1")
    user2_data = UserSerializer(read_only=True, source="user2")
    last_message = serializers.SerializerMethodField()
    user2_image = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = (
            "id",
            "user1",
            "user1_data",
            "user2",
            "user2_data",
            "user2_image",
            "last_message",
            "updated",
            "created_at",
        )

    def create(self, validated_data):
        return Thread.objects.create(**validated_data)

    def get_last_message(self, obj):
        last_message = obj.chat_messages.order_by("-created_at").first()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def get_user2_image(self, obj):
        try:
            return obj.user2.user_profile.get().profile_pic.url
        except:
            return None


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()

    class Meta:
        model = ChatMessage
        fields = "__all__"
