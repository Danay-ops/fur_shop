# Generated by Django 4.2.14 on 2024-07-18 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_address',
            field=models.TextField(blank=True, null=True, verbose_name='Адрес доставки'),
        ),
        migrations.AddField(
            model_name='order',
            name='phone_number',
            field=models.CharField(default=11111, max_length=20, verbose_name='Номер телефона'),
            preserve_default=False,
        ),
    ]
