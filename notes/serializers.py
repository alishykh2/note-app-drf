from rest_framework import serializers

from user.serializers import UserSerializer

from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Note
        fields = "__all__"

    def validate(self, attrs):
        attrs["user"] = self.context["request"].user

        return attrs
