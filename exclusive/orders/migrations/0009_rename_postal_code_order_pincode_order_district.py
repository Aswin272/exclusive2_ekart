# Generated by Django 5.0.3 on 2024-05-12 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_remove_order_address_order_city_order_country_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='postal_code',
            new_name='pincode',
        ),
        migrations.AddField(
            model_name='order',
            name='district',
            field=models.CharField(default='00000', max_length=100),
            preserve_default=False,
        ),
    ]