# Generated by Django 4.2.14 on 2024-07-16 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='cart',
            managers=[
            ],
        ),
        migrations.AlterField(
            model_name='cart',
            name='created_timestamp',
            field=models.DateField(auto_now_add=True, verbose_name='Дата добавления'),
        ),
    ]
