# Generated by Django 3.2.14 on 2023-01-30 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0022_auto_20230130_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='body',
            field=models.TextField(max_length=18000, verbose_name='body'),
        ),
    ]
