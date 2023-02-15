from django.urls import path

from rest_framework import routers

from .views import NoteHistoryViewSet
from .views import NoteViewSet
from .views import RevertNoteViewSet

router = routers.SimpleRouter()
router.register(r"note", NoteViewSet)


urlpatterns = [
    path("note/history/<int:pk>", NoteHistoryViewSet.as_view(), name="share_note"),
    path("note/revert/<int:pk>", RevertNoteViewSet.as_view(), name="share_note"),
]
urlpatterns += router.urls
