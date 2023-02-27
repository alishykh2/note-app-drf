from django.urls import path

from rest_framework import routers

from .views import NoteCommentViewSet
from .views import NoteHistoryViewSet
from .views import NoteViewSet

router = routers.SimpleRouter()
router.register(r"note", NoteViewSet)
router.register(r"note/(?P<note_id>\d+)/comment", NoteCommentViewSet)


urlpatterns = [
    path("note/history/<int:pk>", NoteHistoryViewSet.as_view(), name="share_note"),
]
urlpatterns += router.urls
