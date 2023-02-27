from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Note(models.Model):
    title = models.CharField(max_length=500)
    archive_date = models.DateField(null=True)
    author = models.ForeignKey(User, related_name="author", on_delete=models.CASCADE)
    share_with = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NoteHistory(models.Model):
    title = models.CharField(max_length=500)
    note = models.ForeignKey(
        Note, related_name="version_history", on_delete=models.CASCADE,
    )
    updated_by = models.ForeignKey(
        User,
        related_name="updated_by",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NoteComment(models.Model):
    text = models.CharField(max_length=500)
    note = models.ForeignKey(Note, related_name="comments", on_delete=models.CASCADE)
    comment_by = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
