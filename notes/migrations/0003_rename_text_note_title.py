# Generated by Django 4.1.5 on 2023-02-14 07:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notes", "0002_alter_note_user"),
    ]

    operations = [
        migrations.RenameField(
            model_name="note",
            old_name="text",
            new_name="title",
        ),
    ]