import datetime

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Note
from .models import NoteHistory
from .permissions import IsAuthor
from .serializers import NoteHistorySerializer
from .serializers import NoteSerializer

User = get_user_model()


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    permission_classes = [IsAuthenticated, IsAuthor]
    serializer_class = NoteSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "id"]

    def get_queryset(self):
        type = self.request.query_params.get("type", "")
        today = datetime.datetime.today().strftime("%Y-%m-%d")

        if type == "archive":
            qs = Q(archive_date__lte=today)
        else:
            qs = Q(archive_date__gt=today) | Q(archive_date=None)
        return Note.objects.filter(
            (Q(author=self.request.user) | Q(share_with=self.request.user)),
            qs,
        )


class NoteHistoryViewSet(APIView):
    permission_classes = [IsAuthenticated, IsAuthor]

    def get(self, request, pk, format=None):
        note = NoteHistory.objects.filter(note__id=pk).order_by("-created_at")
        return Response(
            NoteHistorySerializer(note, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, pk, format=None):
        note = get_object_or_404(Note, pk=pk)
        note_history = (
            NoteHistory.objects.filter(note__id=pk).order_by("created_at").first()
        )
        if note_history:
            note.title = note_history.title
            note.save()
            NoteHistory.objects.create(
                note=note,
                title=note.title,
                updated_by=request.user,
            )

        return Response(
            {"message": "Note updated successfully", "data": NoteSerializer(note).data},
            status=status.HTTP_200_OK,
        )


class RevertNoteViewSet(APIView):
    permission_classes = [IsAuthenticated, IsAuthor]

    def post(self, request, pk, format=None):
        note = get_object_or_404(Note, pk=pk)
        note_history = (
            NoteHistory.objects.filter(note__id=pk).order_by("created_at").first()
        )
        if note_history:
            note.title = note_history.title
            note.save()
            NoteHistory.objects.create(
                note=note,
                title=note.title,
                updated_by=request.user,
            )

        return Response(
            {"message": "Note updated successfully", "data": NoteSerializer(note).data},
            status=status.HTTP_200_OK,
        )
