from rest_framework import viewsets
from .serializers import NoteSerializer
from .models import Note
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = NoteSerializer
    lookup_field = "pk"
    filter_backends = [filters.SearchFilter]
    search_fields = ["text", "id"]
