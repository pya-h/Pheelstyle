from os.path import join
from django.db import models
from category.models import Category
from django.urls import reverse
import uuid
from user.models import User


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, blank=False,)
    name_fa = models.CharField(max_length=100, unique=True, blank=False, verbose_name="نام")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=1024, blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='photos/products')
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)
    discount = models.IntegerField(default=0)  # discount in percentage
    # below line delete all products associated when the category deletes!! expected?
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

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


class VariationManager(models.Manager):
    def by_color(self):
        """
            returns color variations
        :return:list
        """
        return super(VariationManager, self).filter(parameter='color', is_available=True)

    def by_size(self):
        """
            returns size variations
        :return:list
        """
        return super(VariationManager, self).filter(parameter='size', is_available=True)

    def displayable(self):
        """
        check if the product has at least one available variation for each defined parameter
        :return:boolean
        """
        # **** add more checking like checking product.stock and product.available
        return self.by_size() and self.by_color()

    def item_exists(self, color, size):
        """
            this will check if a product with these preferred color and size exists in the inventory
            :param color:
            :param size:
            :return:boolean
        """
        color_exists = self.by_color().filter(value=color.lower())
        size_exists = self.by_size().filter(value=size.lower())
        return color_exists and size_exists


class Variation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    variation_parameters = (
        ('color', 'رنگ'),
        ('size', 'سایز')
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # parameter means that on what parameter this variation differs from other variations with same Product
    parameter = models.CharField(max_length=10, choices=variation_parameters)
    value = models.CharField(max_length=20)
    is_available = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now=True)
    stock = models.IntegerField(default=1)  # number of remaining
    # use default value for variation image or not?
    # if variation has no image use the product.image
    image = models.ImageField(upload_to=join('photos/products', parameter.__str__()), blank=True)  # parameter + '_'
    # + value), blank=True)
    # default image in photos/product root folder and variations in /product_name ? huh!
    objects = VariationManager()

    def parameter_fa(self):
        param = self.parameter.lower()
        if param == 'color':
            return 'رنگ'
        elif param == 'size':
            return 'سایز'
        return 'نامشخص!'

    def ID(self):
        return self.id

    def __str__(self):
        return f'{self.parameter_fa()} : {self.value}'


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.fname}: {self.comment}'
