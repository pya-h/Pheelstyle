from user.models import User, Profile
from django import forms


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['fname', 'lname', 'phone', 'email']

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        placeholders = {'fname': 'نام', 'lname': 'نام خانوادگی', 'email': 'ایمیل', 'phone': 'شماره تلفن'}
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = placeholders[field]


class ProfileEditForm(forms.ModelForm):
    avatar = forms.ImageField(required=False, error_messages={'invalid': ("فایل انتخاب کردی نامعتبره!")}, widget=forms.FileInput)

    class Meta:
        model = Profile
        fields = ['province', 'city', 'address', 'avatar', 'postal_code']

    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        placeholders = {'province': 'استان', 'city': 'شهر', 'address': 'آدرس', 'postal_code': 'کد پستی'}
        self.fields['avatar'].widget.attrs['id'] = "fileChangeAvatar"

        for field in placeholders:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = placeholders[field]

        self.fields['address'].widget.attrs['rows'] = 3
        # style the avatar change button:
        self.fields['avatar'].widget.attrs['title'] = "میتونی از اینجا آواتارتو عوض کنی"
        self.fields['avatar'].widget.attrs['class'] = "btn btn-outline-light btn-block btn-shaking text-dark btn-large"
        self.fields['avatar'].widget.attrs['style'] = "cursor: pointer;"
        self.fields['avatar'].widget.attrs['title'] = "میتونی از اینجا آواتارتو عوض کنی"
