# Generated by Django 4.1.7 on 2023-04-04 18:47

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("traits", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="trait",
            old_name="name",
            new_name="trait_name",
        ),
    ]
