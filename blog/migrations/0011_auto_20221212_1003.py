# Generated by Django 3.2.14 on 2022-12-12 13:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_post_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='order',
        ),
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post', to='blog.category'),
        ),
    ]
