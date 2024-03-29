from django.db import models
from user.models import User
import uuid


class Shop(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='آیدی')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False, verbose_name='مالک')
    name = models.CharField(max_length=64, blank=False, null=False, verbose_name='نام (انگلیسی)')
    name_fa = models.CharField(max_length=64, blank=False, null=False, verbose_name='نام (فارسی)')

    description = models.CharField(max_length=1024, blank=True, verbose_name='توضیحات')
    location = models.CharField(max_length=128, blank=False, null=False, verbose_name='آدرس')
    slug = models.SlugField(max_length=64, unique=True, verbose_name='اسلاگ')

    def __str__(self):
        return self.name_fa

    def rating(self):
        pass
        # this will be calculated by the average of shop's products ratings

    class Meta:
        verbose_name = 'فروشگاه'
        verbose_name_plural = 'فروشگاه ها'


class Gallery(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, default=None, verbose_name='فروشگاه')
    image = models.ImageField(upload_to='photos/shops', verbose_name="تصویر")

    class Meta:
        verbose_name = "گالری"
        verbose_name_plural = "گالری"

    def __str__(self):
        return self.shop.name_fa
