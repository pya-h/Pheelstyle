# Generated by Django 3.2.12 on 2022-10-25 21:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sid', models.CharField(blank=True, max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('cost', models.IntegerField(default=0)),
                ('discounts', models.IntegerField(default=0)),
                ('belongs_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TakenProduct',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(default=0)),
                ('is_available', models.BooleanField(default=True)),
                ('exact_stock', models.IntegerField(blank=True, null=True)),
                ('preferred_variations', models.ManyToManyField(blank=True, to='store.Variation')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
                ('stack', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stack.stack')),
            ],
        ),
    ]
