import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from user.serializers import UserSerializer

from .models import Note
from .models import NoteHistory
from .utils import send_email

User = get_user_model()


class NoteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    share_with = serializers.ListSerializer(
        child=serializers.EmailField(),
        write_only=True,
    )

    class Meta:
        model = Note
        fields = "__all__"
        # exclude = ["share_with"]

    def validate(self, attrs):
        if "archive_date" in attrs and attrs["archive_date"]:
            today = datetime.datetime.today()
            date = datetime.datetime.combine(attrs["archive_date"], datetime.time(0, 0))
            if date < today:
                raise serializers.ValidationError("Date must be greater than today.")

        attrs["author"] = self.context["request"].user
        return attrs

    def create(self, validated_data):
        validated_data.pop("share_with")
        note = super(NoteSerializer, self).create(validated_data)
        NoteHistory.objects.create(note=note, title=note.title, updated_by=note.author)
        return note

    def update(self, instance, validated_data):
        self.createVersion(instance, validated_data)
        # user_ids = self.sendEmailNotification(validated_data)
        instance.title = validated_data.get("title", instance.title)
        instance.archive_date = validated_data.get(
            "archive_date",
            instance.archive_date,
        )
        # instance.share_with.add(*user_ids)
        instance.save()
        return instance

    def createVersion(self, instance, validated_data):
        if "title" in validated_data and validated_data["title"] != instance.title:
            note_history = NoteHistory(
                title=instance.title,
                note=instance,
                updated_by=self.context["request"].user,
            )
            note_history.save()

        return instance

    def sendEmailNotification(self, validated_data):
        share_with = validated_data.pop("share_with")
        user_ids = []
        for email in share_with:
            user = get_object_or_404(User, email=email)
            send_email(
                subject="Note Shared",
                message=self.context["request"].user.email + " shared note with you ",
                email=email,
            )
            user_ids.append(user.id)

        return user_ids


class NoteHistorySerializer(serializers.ModelSerializer):
    updated_by = UserSerializer(read_only=True)
    note = NoteSerializer(read_only=True)  # is this necessary?

    class Meta:
        model = NoteHistory
        fields = "__all__"
