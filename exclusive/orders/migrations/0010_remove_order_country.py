# Generated by Django 5.0.3 on 2024-05-12 04:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_rename_postal_code_order_pincode_order_district'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='country',
        ),
    ]
