# Generated by Django 3.2.9 on 2023-05-13 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='نام به اجنبی'),
        ),
    ]