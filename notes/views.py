from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import filters
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
    lookup_field = "pk"
    filter_backends = [filters.SearchFilter]
    search_fields = ["text", "id"]


class NoteShareViewSet(APIView):
    def post(self, request, pk, format=None):
        note = get_object_or_404(Note, pk=pk)
        user = get_object_or_404(User, email=request.data.get("email"))
        send_email(
            subject="Note Shared",
            message=request.user.email + " shared note with you ",
            email=request.data.get("email"),
        )
        note.share.add(user.id)
        note.save()
        return Response({"message": "Note Shared"}, status=status.HTTP_200_OK)
