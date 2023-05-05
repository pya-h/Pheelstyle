from os.path import join
from django.db import models
from category.models import Category
from django.urls import reverse
import uuid
from user.models import User
from django.db.models import Avg, Count


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="آیدی")
    name = models.CharField(max_length=100, unique=True, blank=False, verbose_name="نام به احنبی")
    name_fa = models.CharField(max_length=100, unique=True, blank=False, verbose_name="نام")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="اسلاگ")
    description = models.TextField(max_length=1024, blank=True, verbose_name="مشخصات")
    price = models.IntegerField(verbose_name="شیتیل")
    available = models.BooleanField(default=True, verbose_name="در دسترس؟")
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    modified = models.DateTimeField(auto_now=True, verbose_name="تاریخ تغییر")
    discount = models.IntegerField(default=0, verbose_name="تخفیف")  # discount in percentage
    # below line delete all products associated when the category deletes!! expected?
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="دسته بندی")
    image = models.ImageField(upload_to='photos/products', verbose_name="تصویر")

    class Meta:
        verbose_name = "کالا"
        verbose_name_plural = "کالا ها"

    def update(self):
        # this function must update fields after sth has been sold
        # like updating availability
        # or update dates?
        return self.available  # temp

    # this is IMPORTANT -> remove image from here and add use default variation image

    def url(self):
        return reverse('single_product', args=[self.category.slug, self.slug])

    def ID(self):
        return self.id

    def __str__(self):
        return self.name_fa
        # return self.name_fa

    def format_rating(self):
        reviews = Review.objects.filter(product=self, status=True).aggregate(average_rating=Avg('rating'),
                                                                             count=Count('id'))
        if reviews['count']:
            return f'{float(reviews["average_rating"])}/5.0 [{int(reviews["count"])}]'
        return "-"

    def rating(self):
        try:
            return Review.objects.filter(product=self, status=True).aggregate(average_rating=Avg('rating'))[
                'average_rating']
        except Exception as ex:
            print("Something went wrong while calculating product rating because: ", ex)
        return None


class VariationManager(models.Manager):
    class Meta:
        verbose_name = "سازمان دهنده مشخصات"
        verbose_name_plural = "سازمان دهنده مشخصات"

    def both_separately(self):
        variations = super(VariationManager, self).filter(is_available=True)
        sizes, colors = set(), set()
        for var in variations:
            sizes.add(var.size)
            colors.add(var.color)
        return sizes, colors

    def by_size(self):
        variations = super(VariationManager, self).filter(is_available=True)
        sizes = set()
        for var in variations:
            sizes.add(var.size)
        return sizes

    def by_color(self):
        variations = super(VariationManager, self).filter(is_available=True)
        colors = set()
        for var in variations:
            colors.add(var.color)
        return colors

    def find_specific_color(self, color):
        """
                returns color variations
            :return:list
            """
        return super(VariationManager, self).filter(color=color, is_available=True)

    def find_specific_size(self, size):
        """
                returns size variations
            :return:list
            """
        return super(VariationManager, self).filter(size=size, is_available=True)

    def displayable(self):
        """
            check if the product has at least one available variation for each defined parameter
            :return:boolean
            """
        # **** add more checking like checking product.stock and product.available
        return super(VariationManager, self).all().count() > 0

    def item_exists(self, color, size):
        """
                this will check if a product with these preferred color and size exists in the inventory
                :param color:
                :param size:
                :return:boolean
            """
        return super(VariationManager, self).filter(size=size, color=color).count() > 0

    def variation_count(self, color, size):
        """
                this will check if a product with these preferred color and size exists in the inventory
                :param color:
                :param size:
                :return:boolean
            """
        return super(VariationManager, self).filter(size=size, color=color, is_available=True).count()


class Variation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = "گونه"
        verbose_name_plural = "گونه ها"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="کالای مرتبط")
    # parameter means that on what parameter this variation differs from other variations with same Product
    size = models.CharField(max_length=10, verbose_name="سایز")
    color = models.CharField(max_length=20, verbose_name="رنگ")

    is_available = models.BooleanField(default=True, verbose_name="در دسترس؟")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    stock = models.IntegerField(default=0, verbose_name="موجودی")  # number of remaining
    objects = VariationManager()

    def ID(self):
        return self.id

    def __str__(self):
        return f'{self.product} - {self.size} : {self.color}'


class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=None, verbose_name="کالای مرتبط")
    image = models.ImageField(upload_to='photos/products', verbose_name="تصویر")

    class Meta:
        verbose_name = "گالری"
        verbose_name_plural = "گالری"

    def __str__(self):
        return self.product.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="کالای مرتبط")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    comment = models.TextField(max_length=500, blank=True, verbose_name="سخنوری")
    rating = models.FloatField(verbose_name="امتیازدهی")
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True, verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ درافشانی")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="به روز رسانی نظز")

    class Meta:
        verbose_name = 'فیلان بیسار'
        verbose_name_plural = 'فیلان ها و بیسارها'

    def __str__(self):
        return f'{self.user.fname}: {self.comment}'
