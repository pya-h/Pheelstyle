# Generated by Django 3.2.9 on 2023-05-21 13:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('purchase', '0012_alter_order_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='DevShare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=0, verbose_name='مبلغ سهم')),
                ('status', models.CharField(choices=[('onhold', 'در انتظار پرداخت'), ('verified', 'قطعی')], default='onhold', max_length=20)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='purchase.order')),
            ],
        ),
    ]