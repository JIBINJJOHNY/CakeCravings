# Generated by Django 4.2.7 on 2023-12-11 21:08

from django.db import migrations
import shortuuid.django_fields


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_status_alter_order_zip_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_id',
            field=shortuuid.django_fields.ShortUUIDField(alphabet='abcdefgh12345', length=22, max_length=30, prefix='cc', unique=True),
        ),
    ]