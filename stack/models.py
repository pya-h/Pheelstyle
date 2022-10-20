import uuid
from store.models import Product, Variation
from django.db import models
from user.models import User


class Stack(models.Model):
    sid = models.CharField(max_length=50, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    belongs_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    cost = models.IntegerField(default=0)  # total value (total price)
    discounts = models.IntegerField(default=0)

    def final_cost(self):
        result = self.cost - self.discounts
        int_result = int(result)
        return int_result if result == int_result else  self.cost - self.discounts

    def __str__(self):
        return self.sid

    def ID(self):
        return self.sid

    def submit_bill(self):  # stack_owner ==> request.user
        self.cost = self.discounts = 0
        try:
            # if stack_owner.is_authenticated:
            #    takens = TakenProduct.objects.all().filter(stack__belongs_to=stack_owner).filter(is_available=True)
            # else:
            #    takens = TakenProduct.objects.all().filter(stack=self).filter(is_available=True)
            takens = TakenProduct.objects.all().filter(stack=self).filter(is_available=True)
            # calculate costs:
            for taken in takens:
                self.cost += taken.total_price()
                self.discounts += taken.total_discount()

            self.save()
        except TakenProduct.DoesNotExist:
            return {
                'stack': self,
                'taken_products': []
            }

        return {
            'stack': self,
            'taken_products': takens
        }


class TakenProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # match th item whit selected product
    preferred_variations = models.ManyToManyField(Variation, blank=True)
    stack = models.ForeignKey(Stack, on_delete=models.CASCADE)  # to which shop stack it belongs
    quantity = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    exact_stock = models.IntegerField(blank=True, null=True)  # number of remaining

    def update_exact_stock(self):
        variations = list(self.preferred_variations.all())
        self.exact_stock = variations[0].stock
        for variation in variations:
            if self.exact_stock > variation.stock:
                self.exact_stock = variation.stock

    def increase_quantity(self):
        self.update_exact_stock()  # to make sure exact stock is updated for latest variations
        if self.product.available and self.quantity < self.exact_stock:
            self.quantity += 1
        # else:
        # SHOW ERROR MESSAGE

    def decrease_quantity(self):
        self.quantity = self.quantity - 1 if self.quantity > 0 else 0

    def ID(self):
        return self.id

    def total_price(self):  # the price of all items of this product(and variation) without considering discounts
        return self.quantity * self.product.price

    def absolute_price(self):  # each item price considering the discounts
        return int(self.product.price * (100 - self.product.discount) / 100)

    def final_price(self):  # absolute price considering the quantity of the item and discounts
        return self.absolute_price() * self.quantity

    def total_discount(self):
        result = self.total_price() * self.product.discount / 100
        int_result = int(result)
        return int_result if int_result == result else result

    def __str__(self):
        return '%s [%d]' % (self.product.__str__(), self.quantity)

    def __unicode__(self):
        return self.product
