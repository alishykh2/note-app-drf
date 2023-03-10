# Generated by Django 4.1.5 on 2023-02-14 19:28

from django.db import migrations
from django.db import models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("notes", "0004_rename_user_note_author_note_share"),
    ]

    operations = [
        migrations.AddField(
            model_name="note",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="note",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
