# Generated by Django 4.1.5 on 2023-02-15 12:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notes", "0007_alter_note_author_notehistory"),
    ]

    operations = [
        migrations.RenameField(
            model_name="notehistory",
            old_name="note_id",
            new_name="note",
        ),
    ]