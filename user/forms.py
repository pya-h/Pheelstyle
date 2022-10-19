from django import forms
from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    placeholders = {'fname': 'نام', 'lname': 'نام خانوادگی', 'email': 'ایمیل', 'phone': 'شماره تلفن', 'password': 'رمزعبور',
                    'confirm_password': 'تایید رمزعبور'}

    class Meta:
        model = User
        fields = ['fname', 'lname', 'phone', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = self.placeholders[field]

    # this method is for data validation, wrong account data will raise errors
    def clean(self):
        # get sent form's data to start checking
        cleaned_data = super(RegisterForm, self).clean()
        InputValidator.full(cleaned_data)


class InputValidator:
    # validator of registration and ... input data
    @staticmethod
    def password_check(password):
        if len(password) < 6:  # check password is strong and at least 6 characters
            raise forms.ValidationError('رمزعبور باید حداقل ۶ کاراکتر باشد.')

        # check if there's alpha character is the password
        low_alphabet = 'abcdefghijklmnopqrstuvwxyz'
        high_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        has_alphabet = False
        for ch in password:
            if ch in low_alphabet or ch in high_alphabet:
                has_alphabet = True
                break
        if not has_alphabet:
            raise forms.ValidationError('رمزعبور باید شامل حداقل یک حرف الفبای انگلیسی باشد.')

        digits = '0123456789'
        has_digits = False
        for ch in password:
            if ch in digits:
                has_digits = True
                break
        if not has_digits:
            raise forms.ValidationError('رمزعبور باید شامل حداقل یک عدد باشد.')

    @staticmethod
    def full(data):
        phone = data.get('phone')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if len(email) < 3:  # check username length
            raise forms.ValidationError('ایمیل باید حداقل ۳ کاراکتر باشد.')
        if not phone.isdigit():  # check if username is valid text and not a number
            raise forms.ValidationError('شماره تلفن شما نامعتبر است.')
        if phone and User.objects.filter(phone=phone).count():  # if there is a account with this email/phone number
            raise forms.ValidationError("کاربری با این شماره تلفن قبلا ثبت نام کرده است.")
        if email and User.objects.filter(email__iexact=email).count():  # if there is a account with this username
            raise forms.ValidationError("کاربری با این ایمیل قبلا ثبت نام کرده است.")
        if password != confirm_password:  # check if both passwords match
            raise forms.ValidationError('رمزعبورها مطابقت ندارند.')
        InputValidator.password_check(password=password)
