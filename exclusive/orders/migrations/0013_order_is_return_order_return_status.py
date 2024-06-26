# Generated by Django 5.0.3 on 2024-05-15 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_remove_orderitem_is_cancelled_order_is_cancelled'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_return',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='return_status',
            field=models.CharField(choices=[('Return Requested', 'Return Requested'), ('Returned', 'Returned'), ('Rejected', 'Rejected')], default='Return Requested', max_length=100),
        ),
    ]
