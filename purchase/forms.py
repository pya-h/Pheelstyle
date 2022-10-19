from django import forms
from .models import OrderReceiver, Receipt


class OrderForm(forms.ModelForm):
    notes = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = OrderReceiver
        fields = ['fname', 'lname', 'phone', 'province', 'city', 'address', 'postal_code']

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)

    # this method is for data validation, wrong account data will raise errors
    def clean(self):
        # get sent form's data to start checking
        cleaned_data = super(OrderForm, self).clean()
        print('order form clean method has been called')
        # InputValidator.full(cleaned_data)


class ReserveTransactionForm(forms.ModelForm):

    class Meta:
        model = Receipt
        fields = ['amount', 'image', 'reference_id', 'order_key']

    def __init__(self, *args, **kwargs):
        super(ReserveTransactionForm, self).__init__(*args, **kwargs)

    def clean(self):
        # get sent form's data to start checking
        print("clean method called")
        cleaned_data = super(ReserveTransactionForm, self).clean()
        print(cleaned_data)
        #if cleaned_data.get('amount') <= 0:
            #raise forms.ValidationError('مقدار تراکنش باید بزرگتر از صفر باشد!')
