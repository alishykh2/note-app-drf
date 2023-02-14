from rest_framework import routers

from .views import NoteViewSet

router = routers.SimpleRouter()
router.register(r"note", NoteViewSet)


urlpatterns = []
urlpatterns += router.urls
