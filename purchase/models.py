from django.db import models

from store.models import Variation, Product
from user.models import User
from uuid import uuid4
from django.urls import reverse


class Receipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    reference_id = models.CharField(max_length=30)  # *** WHAT TO SET ON MAX_LENGTH ??
    image = models.ImageField(upload_to='photos/transactions', blank=True, null=True)
    amount = models.IntegerField(verbose_name="Transaction Amount")
    order_key = models.CharField(max_length=20)  # this is the order checking code between seller and buyer

    def __str__(self):
        return self.reference_id


class Transaction(models.Model):
    METHODS = (('reserve', 'رزرو'),
              ('zarinpal', 'زرین پال'),
              ('bank_portal', 'درگاه پرداخت بانکی'))
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    VALIDATION_STATUS = (('pending', 'در دست بررسی'), ('valid', 'معتبر'), ('invalid', 'نامعتبر'))
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, blank=True, null=True)
    validation = models.CharField(max_length=20, choices=VALIDATION_STATUS, default='pending')

    performer = models.ForeignKey(User, on_delete=models.CASCADE)
    method = models.CharField(max_length=20, blank=False, choices=METHODS)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.receipt.__str__() if self.receipt.__str__() else "Uncertified"


class OrderReceiver(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    related_to = models.ForeignKey(User, on_delete=models.CASCADE)
    # receiver identification
    fname = models.CharField(max_length=30, verbose_name="Receiver's First Name", blank=True)
    lname = models.CharField(max_length=30, verbose_name="Receiver's Last Name", blank=True)
    phone = models.CharField(max_length=11, verbose_name="Receiver's Phone Number", blank=True)
    # receiver address
    postal_code = models.CharField(max_length=10, verbose_name="Postal Code", blank=False)
    province = models.CharField(max_length=30, verbose_name="Province", blank=False)
    city = models.CharField(max_length=30, verbose_name="City", blank=False)
    address = models.CharField(max_length=256, verbose_name="Address", blank=False)

    def fullname(self):
        return f'{self.fname} {self.lname}'

    def __str__(self):
        return self.fullname()

    def full_address(self):
        return f'{self.province} - {self.city} - {self.address}'


class Order(models.Model):
    # order possible status
    STATUS = (('new', 'جدید'),
              ('pending', 'در دست بررسی'),
              ('certified', 'سفارش معتبر'),
              ('sent', ' ارسال شده'),
              ('delivered', 'تحویل شده'),
              ('separator', '--------------------'),

              ('uncertified', 'سفارش نامعتبر'),
              ('not_sent', 'عدم ارسال'),
              ('undelivered', 'عدم تحویل'),
              ('canceled', 'داستان'),
              ('failed', 'قطعی آب'))
    # model connections
    # EDIT ON_DELETE s
    key = models.CharField(max_length=20)  # this is the order checking code between seller and buyer
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # is it a good thing to remove records ?
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    receiver = models.ForeignKey(OrderReceiver, on_delete=models.PROTECT)  # edit the on_delete

    # optionals
    notes = models.CharField(max_length=256, verbose_name="Order Notes", blank=True)

    # stats
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    # is_certified = models.BooleanField(default=False)
    # is_delivered = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS, default='new')

    # prices and costs
    cost = models.IntegerField(default=0)  # total value (total price)
    discounts = models.IntegerField(default=0)  # sum of the amount of discounts in Money (not percentage)
    shipping_cost = models.IntegerField(default=0)
    must_be_paid = models.IntegerField(default=0)

    def how_much_to_pay(self):
        self.must_be_paid = self.cost - self.discounts + self.shipping_cost

    def __str__(self):
        return 'سفارشی به نام' + self.receiver.fullname()

    def check_url(self):
        return reverse('check_order', args=[self.key])

    def accept_url(self):
        return reverse('accept_order', args=[self.key])

    def receipt_url(self):
        return reverse('order_receipt', args=[self.key])

    def sell_products(self):
        # apply order and update the product stocks and statistics in the inventory
        ordered_products = OrderedProduct.objects.filter(order=self, buyer=self.buyer,) # transaction=self.transaction
        for item in ordered_products:
            preferred_variations = item.variations.all()
            for preferred_variation in preferred_variations:
                variation = Variation.objects.get(id=preferred_variation.id)
                variation.stock -= item.quantity
                variation.save()
        self.save()


class OrderedProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # match th item whit selected product
    variations = models.ManyToManyField(Variation, blank=True)

    quantity = models.IntegerField(default=0)
    color = models.CharField(max_length=20)  # these two variation are defined separately are for direct access
    size = models.CharField(max_length=20)
    cost = models.IntegerField()  # final price for each product that is ordered ( considering the quantity and discount)

    delivered = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    anything_wrong = models.CharField(max_length=50, blank=True, null=True, default="")

    def __str__(self):
        return f'{self.product.__str__()} {self.color} {self.size} [{self.quantity}]'

    def exact_stock(self):  # even after saving the order etc. => ordered product can get the exact stock value updated by today
        variations = list(self.variations.all())
        es = variations[0].stock
        for variation in variations:
            if es > variation.stock:
                es = variation.stock
        return es

    def resources_are_enough(self):
        return self.exact_stock() >= self.quantity

    def ID(self):
        return self.id

    def total_price(self):  # the price of all items of this product(and variation) without considering discounts
        return self.quantity * self.product.price

    def absolute_price(self):  # each item price considering the discounts
        return int(self.product.price * (100 - self.product.discount) / 100)

    def final_price(self):  # absolute price considering the quantity of the item and discounts
        return self.absolute_price() * self.quantity

    def total_discount(self):
        return self.total_price() * self.product.discount / 100

    def __unicode__(self):
        return self.product
