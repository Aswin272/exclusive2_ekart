# Generated by Django 5.0.3 on 2024-05-06 16:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_categoryoffer_productoffer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='categoryoffer',
            old_name='catgoty',
            new_name='category',
        ),
    ]
