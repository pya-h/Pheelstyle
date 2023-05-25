from django.db import models
from user.models import User
import uuid

# Create your models here.
class Shop(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=64, blank=False, null=False)
    name_fa = models.CharField(max_length=64, blank=False, null=False)

    description = models.CharField(max_length=1024, blank=True)
    location = models.CharField(max_length=128, blank=False, null=False)
    slug = models.SlugField(max_length=64, unique=True)

    def rating(self):
        pass
        # this will be calculated by the average of shop's products ratings



class Gallery(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, default=None)
    image = models.ImageField(upload_to='photos/shops', verbose_name="تصویر")

    class Meta:
        verbose_name = "گالری"
        verbose_name_plural = "گالری"

    def __str__(self):
        return self.shop.name_fa
