# Generated by Django 3.2.9 on 2022-11-04 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_product_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gallery',
            name='image',
        ),
        migrations.AddField(
            model_name='gallery',
            name='images',
            field=models.ImageField(default='3.jpg', max_length=255, upload_to='photos/products'),
            preserve_default=False,
        ),
    ]
