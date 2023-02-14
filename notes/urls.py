from django.urls import path

from rest_framework import routers

from .views import NoteShareViewSet
from .views import NoteViewSet

router = routers.SimpleRouter()
router.register(r"note", NoteViewSet)


urlpatterns = [
    path("note-share/<int:pk>", NoteShareViewSet.as_view(), name="share_note"),
]
urlpatterns += router.urls
