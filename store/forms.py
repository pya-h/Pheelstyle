from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment', 'rating']

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)

    # this method is for data validation, wrong account data will raise errors
    def clean(self):
        # get sent form's data to start checking
        cleaned_data = super(ReviewForm, self).clean()
        print('review form clean method has been called')
