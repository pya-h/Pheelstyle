from django.db import models
import datetime
from store.models import Variation, Product
from user.models import User
from uuid import uuid4
from django.urls import reverse

ORDER_STATUS = {
    'new': 'جدید',
    'pending': 'در دست بررسی',
    'verified': 'سفارش معتبر',
    'indebt': 'شامل بدهی',
    'sent': ' ارسال شده',
    'delivered': 'تحویل شده',
    'refused': 'سفارش نامعتبر',
    'not_sent': 'عدم ارسال',
    'undelivered': 'عدم تحویل',
    'canceled': 'داستان',
    'failed': 'قطعی آب'
}


class Receipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, verbose_name='آیدی')
    reference_id = models.CharField(max_length=30, verbose_name='کد رهیگیری')  # *** WHAT TO SET ON MAX_LENGTH ??
    image = models.ImageField(upload_to='photos/transactions', blank=True, null=True, verbose_name='تصویر')
    amount = models.IntegerField(verbose_name="مقدار تراکنش")
    order_key = models.CharField(max_length=20, verbose_name='شماره سفارش')  # this is the order checking code between seller and buyer

    class Meta:
        verbose_name = 'رسید'
        verbose_name_plural = 'رسیدها'

    def __str__(self):
        return self.reference_id


class Transaction(models.Model):
    METHODS = (('reserve', 'رزرو'),
              ('zarinpal', 'زرین پال'),
              ('bank_portal', 'درگاه پرداخت بانکی'))
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, verbose_name='آیدی')
    VALIDATION_STATUS = (('pending', 'در دست بررسی'), ('valid', 'معتبر'), ('invalid', 'نامعتبر'))
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, blank=True, null=True, verbose_name='رسید')
    validation = models.CharField(max_length=20, choices=VALIDATION_STATUS, default='pending', verbose_name='صحت تراکنش')

    performer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='زدوبند کننده')
    method = models.CharField(max_length=20, blank=False, choices=METHODS, verbose_name='روش پرداخت')
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش ها'

    def __str__(self):
        return self.receipt.__str__() if self.receipt.__str__() else "Uncertified"


class OrderReceiver(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, verbose_name='آیدی')
    related_to = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر مربوطه')
    # order = models.ForeignKey(Order, on_delete=models.CASCADE)
    # receiver identification
    fname = models.CharField(max_length=30, blank=True, verbose_name='اسم')
    lname = models.CharField(max_length=30, blank=True, verbose_name='فامیلی')
    phone = models.CharField(max_length=11, blank=True, verbose_name='تیلیف')
    # receiver address
    postal_code = models.CharField(max_length=10, verbose_name="کد پستی", blank=False)
    province = models.CharField(max_length=30, verbose_name="استان", blank=False)
    city = models.CharField(max_length=30, verbose_name="شهرستان", blank=False)
    address = models.TextField(max_length=256, verbose_name="نشونی", blank=False)

    class Meta:
        verbose_name = 'گیرنده سفارش'
        verbose_name_plural = 'گیرنده های سفارش'

    def fullname(self):
        return f'{self.fname} {self.lname}'

    def __str__(self):
        return self.fullname()

    def full_address(self):
        return f'{self.province} - {self.city} - {self.address}'


class Order(models.Model):
    # order possible status

    STATUS = (('new', ORDER_STATUS['new']),
              ('pending', ORDER_STATUS['pending']),
              ('verified', ORDER_STATUS['verified']),
              ('indebt', ORDER_STATUS['indebt']),
              ('sent', ORDER_STATUS['sent']),
              ('delivered', ORDER_STATUS['delivered']),

              ('separator', '--------------------'),

              ('invalid', ORDER_STATUS['refused']),
              ('not_sent', ORDER_STATUS['not_sent']),
              ('undelivered', ORDER_STATUS['undelivered']),
              ('canceled', ORDER_STATUS['canceled']),
              ('failed', ORDER_STATUS['failed']))
    # model connections
    # EDIT ON_DELETE s
    key = models.CharField(max_length=20, verbose_name='شماره سفارش')  # this is the order checking code between seller and buyer
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='مالک زدوبند')  # is it a good thing to remove records ?
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='تراکنش')
    receiver = models.ForeignKey(OrderReceiver, on_delete=models.PROTECT, verbose_name='گیرنده')  # edit the on_delete

    # optionals
    notes = models.CharField(max_length=256, verbose_name="لحاظیات", blank=True, null=True)

    # stats
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    date_updated = models.DateTimeField(auto_now=True, verbose_name='تاریخ به روزرسانی')
    # is_certified = models.BooleanField(default=False)
    # is_delivered = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS, default='new', verbose_name='وضعیت')

    # prices and costs
    cost = models.IntegerField(default=0, verbose_name='هزینه')  # total value (total price)
    discounts = models.IntegerField(default=0, verbose_name='تخفیفی جات')  # sum of the amount of discounts in Money (not percentage)
    shipping_cost = models.IntegerField(default=0, verbose_name='هزینه ارسال')
    must_be_paid = models.IntegerField(default=0, verbose_name='هزینه نهایی')
    seen = models.BooleanField(default=False, verbose_name='مشاهده توسط ادمین')
    whats_wrong = models.TextField(max_length=256, null=True, blank=True, verbose_name='علت رد سفارش')

    class Meta:
        verbose_name = 'زدوبند'
        verbose_name_plural = 'زدوبندها'

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

    def keygen(self):
        # now I generate the order key: the key that that identifies the order for both seller and buyer
        year = int(datetime.date.today().strftime('%Y'))
        month = int(datetime.date.today().strftime('%m'))
        day = int(datetime.date.today().strftime('%d'))
        today = datetime.date(year, month, day)  # construct today's date in proper format and object
        return today.strftime('%Y%m%d') + str(self.id)  # django default primary key: id starts from 1 increasing by one

    def sell_products(self):
        # apply order and update the product stocks and statistics in the inventory
        ordered_products = PurchasedItem.objects.filter(order=self, buyer=self.buyer, )  # transaction=self.transaction
        for item in ordered_products:
            preferred_variations = item.variations.all()
            for preferred_variation in preferred_variations:
                variation = Variation.objects.get(id=preferred_variation.id)
                variation.stock -= item.quantity
                variation.save()
        self.save()

    def status_fa(self):
        return ORDER_STATUS[str(self.status)]


class PurchasedItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, verbose_name='آیدی')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='سفارش مربوطه')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='مالک زدوبند')

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='کالا')  # match th item whit selected product
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE, verbose_name='گونه')

    quantity = models.IntegerField(default=0, verbose_name='تعداد')
#    color = models.CharField(max_length=20, verbose_name='رنگ')  # these two variation are defined separately are for direct access
#    size = models.CharField(max_length=20, verbose_name='سایز')
    cost = models.IntegerField(verbose_name='هزینه')  # final price for each product that is ordered ( considering the quantity and
    # discount)

    delivered = models.BooleanField(default=False, verbose_name='تحویل شده')
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    date_updated = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ به روزرسانی')
    anything_wrong = models.CharField(max_length=50, blank=True, null=True, default="", verbose_name='مشکل پشکل؟')

    class Meta:
        verbose_name = 'کالای زدوبندی'
        verbose_name_plural = 'کالاهای زدوبندی'

    def __str__(self):
        return f'{self.product} - {self.variation} [{self.quantity}]'

    def resources_are_enough(self):
        return self.variation.stock >= self.quantity

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
