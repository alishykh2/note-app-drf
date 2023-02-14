from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Note(models.Model):
    title = models.CharField(max_length=500)
    archive_date = models.DateField(null=True)
    author = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)
    share = models.ManyToManyField(User)
