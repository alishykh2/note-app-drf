import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from user.serializers import UserSerializer

from .models import Note
from .utils import send_email

User = get_user_model()


class NoteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    share_with = serializers.ListSerializer(
        child=serializers.CharField(),
        write_only=True,
    )

    class Meta:
        model = Note
        fields = "__all__"
        # exclude = ["share_with"]

    def validate(self, attrs):
        today = datetime.datetime.today()
        date = datetime.datetime.combine(attrs["archive_date"], datetime.time(0, 0))
        if date < today:
            raise serializers.ValidationError("Date must be greater than today.")

        attrs["author"] = self.context["request"].user
        return attrs

    def create(self, validated_data):
        share_with = validated_data.pop("share_with")
        print(share_with)
        obj = Note.objects.create(**validated_data)
        obj.save(foo=validated_data["foo"])
        return obj

    def update(self, instance, validated_data):
        share_with = validated_data.pop("share_with")
        print(share_with)
        user_ids = []
        for email in share_with:
            user = get_object_or_404(User, email=email)
            send_email(
                subject="Note Shared",
                message=self.context["request"].user.email + " shared note with you ",
                email=email,
            )
            user_ids.append(user.id)
        instance.title = validated_data["title"]
        instance.archive_date = validated_data["archive_date"]

        instance.share_with.add(*user_ids)
        instance.save()
        return instance
