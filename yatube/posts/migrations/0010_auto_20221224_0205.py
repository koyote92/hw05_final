# Generated by Django 2.2.16 on 2022-12-23 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20221224_0203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, help_text='Дата публикации комментария', verbose_name='Дата комментария'),
        ),
    ]