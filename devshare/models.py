from django.db import models
from purchase.models import Order

dev_coefficient = 0.05


# Create your models here.
class DevShare(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=False)
    STATUS = (('onhold', 'در انتظار پرداخت'),
              ('verified', 'قطعی'))
    amount = models.IntegerField(verbose_name='مبلغ سهم', default=0)
    status = models.CharField(max_length=20, choices=STATUS, default='onhold')

    def calculate(self):
        self.amount = self.order.must_be_paid * dev_coefficient

    def verify(self):
        self.status = 'verified'
