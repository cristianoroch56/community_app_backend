from rest_framework import serializers
from events.models import Events


class EventSerializers(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = "__all__"

    def to_representation(self, instance):
        user = self.context.get("user")
        representation = super().to_representation(instance)
        is_liked = representation.get("liked_by", [])
        is_bookmarked = representation.get("bookmarked_by", [])

        representation["liked_by"] = bool(user in is_liked)
        representation["bookmarked_by"] = bool(user in is_bookmarked)

        return representation
