from django.db import models
from django.contrib.auth import get_user_model

# from authentication.models import User

User = get_user_model()


class Note(models.Model):
    text = models.CharField(max_length=500)
    archive_date = models.DateField(null=True)
    user = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)
