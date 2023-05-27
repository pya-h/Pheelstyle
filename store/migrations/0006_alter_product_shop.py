# Generated by Django 3.2.9 on 2023-05-24 21:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_alter_shop_id'),
        ('store', '0005_alter_product_shop'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='shop',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='shop.shop'),
            preserve_default=False,
        ),
    ]