# Generated by Django 3.2.25 on 2025-03-01 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0005_alter_area_layer'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockinformdetail',
            name='packing_type',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
