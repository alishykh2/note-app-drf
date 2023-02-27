import datetime

from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Note
from .models import NoteComment
from .models import NoteHistory
from .permissions import IsAuthor
from .permissions import IsSharedWith
from .serializers import NoteCommentSerializer
from .serializers import NoteHistorySerializer
from .serializers import NoteSerializer

User = get_user_model()


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    permission_classes = [IsAuthenticated, IsAuthor | IsSharedWith]
    serializer_class = NoteSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "id"]
    pagination_class = PageNumberPagination
    page_size = 10

    def get_queryset(self):
        type = self.request.query_params.get("type", "")
        today = datetime.datetime.today().strftime("%Y-%m-%d")

        if type == "archive":
            qs = Q(archive_date__lte=today)
        else:
            qs = Q(archive_date__gt=today) | Q(archive_date=None)
        return (
            Note.objects.filter(
                (Q(author=self.request.user) | Q(share_with=self.request.user)),
                qs,
            )
            .select_related("author")
            .prefetch_related(
                Prefetch(
                    "comments",
                    queryset=NoteComment.objects.order_by("-created_at").select_related(
                        "comment_by",
                    ),
                    to_attr="user_comments",
                ),
                "share_with",
                Prefetch(
                    "version_history",
                    queryset=NoteHistory.objects.order_by("-created_at").select_related(
                        "updated_by",
                    ),
                    to_attr="note_version_history",
                ),
            )
        )


class NoteHistoryViewSet(APIView):
    permission_classes = [IsAuthenticated, IsAuthor | IsSharedWith]

    def get(self, request, pk, format=None):
        note_history = (
            NoteHistory.objects.filter(note__id=pk)
            .order_by("-created_at")
            .select_related("updated_by")
        )
        return Response(
            NoteHistorySerializer(note_history, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, pk):
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
            {
                "message": "Note updated successfully",
            },
            status=status.HTTP_200_OK,
        )


class NoteCommentViewSet(viewsets.ModelViewSet):
    queryset = NoteComment.objects.all()
    permission_classes = [IsAuthenticated, (IsAuthor or IsSharedWith)]
    serializer_class = NoteCommentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["text", "id"]
    pagination_class = PageNumberPagination
    page_size = 10

    def get_queryset(self):
        note_id = self.request.parser_context.get("kwargs", {})["note_id"]
        qs = Q()
        user = self.request.user
        if note_id:
            qs = Q(note__id=note_id)
        return NoteComment.objects.filter(
            qs,
            (Q(note__author=user) | Q(note__share_with=user)),
        ).select_related("comment_by")

    def create(self, request, *args, **kwargs):
        note_id = kwargs["note_id"]

        note = get_object_or_404(Note, id=note_id)
        if note.author == request.user or request.user in note.share_with.all():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(note=note)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"error": "You are not authorized to create a comment on this note."},
                status=status.HTTP_403_FORBIDDEN,
            )
