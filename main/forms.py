from django import forms


class UpdateProfile(forms.Form):
    first_name = forms.CharField(required=False, label='first_name', max_length=200)
    last_name = forms.CharField(required=False, label='last_name', max_length=200)
    email = forms.CharField(label='email', max_length=200)
    city = forms.CharField(required=False, label='city', max_length=200)
    avatar = forms.ImageField(required=False)
