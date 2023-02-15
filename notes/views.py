import datetime

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Note
from .serializers import NoteSerializer
from .utils import send_email

User = get_user_model()


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = NoteSerializer

    def get_queryset(self):
        query = self.request.query_params.get("search", "")
        type = self.request.query_params.get("type", "")
        today = datetime.datetime.today().strftime("%Y-%m-%d")

        if type == "archive":
            qs = Q(archive_date__lte=today)
        else:
            qs = Q(archive_date__gt=today) | Q(archive_date=None)
        return Note.objects.filter(
            Q(title__icontains=query)
            & (Q(author=self.request.user) | Q(share_with=self.request.user)),
            qs,
        )


class NoteShareViewSet(APIView):
    def post(self, request, pk, format=None):
        note = get_object_or_404(Note, pk=pk)
        if note.author != request.user:
            return Response(
                {"message": "Permission Denied"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = get_object_or_404(User, email=request.data.get("email"))
        send_email(
            subject="Note Shared",
            message=request.user.email + " shared note with you ",
            email=request.data.get("email"),
        )
        note.share_with.add(user.id)
        note.save()
        return Response({"message": "Note Shared"}, status=status.HTTP_200_OK)
