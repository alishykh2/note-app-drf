from rest_framework import filters
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = NoteSerializer
    lookup_field = "pk"
    filter_backends = [filters.SearchFilter]
    search_fields = ["text", "id"]
