# Generated by Django 2.0.5 on 2018-05-05 20:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20180505_1904'),
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='comments',
            new_name='Comment',
        ),
    ]
