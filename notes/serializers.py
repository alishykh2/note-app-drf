from rest_framework import serializers
from .models import Note
from authentication.serializers import UserSerializer


class NoteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Note
        fields = "__all__"

    def create(self, validated_data):
        note = Note(
            text=validated_data["text"],
            archive_date=validated_data["archive_date"],
            user=self.context["request"].user,
        )
        note.save()

        return note
