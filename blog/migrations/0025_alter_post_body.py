# Generated by Django 3.2.14 on 2023-01-31 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0024_alter_post_body'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='body',
            field=models.TextField(max_length=20000, verbose_name='body'),
        ),
    ]
