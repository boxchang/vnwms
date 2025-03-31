# Generated by Django 3.2.25 on 2025-03-31 18:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0007_bin_value_item_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='bin_value_history',
            name='item_type',
            field=models.ForeignKey(default='PACKING_OUTERBOX', on_delete=django.db.models.deletion.DO_NOTHING, related_name='bin_value_hist_itemtype', to='warehouse.itemtype'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bin_value',
            name='item_type',
            field=models.ForeignKey(default='PACKING_OUTERBOX', on_delete=django.db.models.deletion.DO_NOTHING, related_name='bin_value_itemtype', to='warehouse.itemtype'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='stockoutform',
            name='item_type',
            field=models.ForeignKey(default='PACKING_OUTERBOX', on_delete=django.db.models.deletion.DO_NOTHING, related_name='stockout_itemtype', to='warehouse.itemtype'),
            preserve_default=False,
        ),
    ]
