# Generated by Django 5.0.3 on 2024-05-05 09:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminn', '0001_initial'),
        ('orders', '0005_orderitem_is_cancelled_orderitem_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminn.coupon'),
        ),
    ]
