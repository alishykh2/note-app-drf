import datetime

from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Note
from .serializers import NoteSerializer

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
