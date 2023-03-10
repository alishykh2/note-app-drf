import datetime

from django.contrib.auth import get_user_model
from django.db import connection
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from user.serializers import UserSerializer

from .models import Note
from .models import NoteComment
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

    def validate(self, attrs):
        if "archive_date" in attrs and attrs["archive_date"]:
            today = datetime.datetime.today()
            date = datetime.datetime.combine(attrs["archive_date"], datetime.time(0, 0))
            if date < today:
                raise serializers.ValidationError("Date must be greater than today.")

        attrs["author"] = self.context["request"].user
        return attrs

    def create(self, validated_data):
        user_ids = self.sendEmailNotification(validated_data)

        note = super(NoteSerializer, self).create(validated_data)
        NoteHistory.objects.create(note=note, title=note.title, updated_by=note.author)
        note.share_with.add(*user_ids)

        return note

    def update(self, instance, validated_data):
        self.createVersion(instance, validated_data)
        user_ids = self.sendEmailNotification(validated_data)
        instance.title = validated_data.get("title", instance.title)
        instance.archive_date = validated_data.get(
            "archive_date",
            instance.archive_date,
        )
        instance.share_with.add(*user_ids)
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

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if "pk" not in self.context.get("request").parser_context.get("kwargs", {}):
            counts = instance.comments.count()
            response["comments"] = {
                "count": counts,
                "comment": NoteCommentSerializer(instance.user_comments[-1]).data
                if counts
                else {},
            }

        else:
            response["comments"] = {
                "count": instance.comments.count(),
                "comments": NoteCommentSerializer(
                    instance.user_comments[:10],
                    many=True,
                ).data,
            }
            response["versions"] = NoteHistorySerializer(
                instance.note_version_history[:10],
                many=True,
            ).data
            response["share_with"] = UserSerializer(instance.share_with, many=True).data
        print(len(connection.queries))

        return response


class NoteHistorySerializer(serializers.ModelSerializer):
    updated_by = UserSerializer(read_only=True)
    # note = NoteSerializer(read_only=True)  # is this necessary?

    class Meta:
        model = NoteHistory
        fields = "__all__"


class NoteCommentSerializer(serializers.ModelSerializer):
    comment_by = UserSerializer(read_only=True)

    class Meta:
        model = NoteComment
        fields = "__all__"

    def validate(self, attrs):
        attrs["comment_by"] = self.context["request"].user
        return attrs
