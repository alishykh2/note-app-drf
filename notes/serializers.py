from rest_framework import serializers

from user.serializers import UserSerializer

from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Note
        exclude = ["share"]

    def validate(self, attrs):
        attrs["author"] = self.context["request"].user
        return attrs
