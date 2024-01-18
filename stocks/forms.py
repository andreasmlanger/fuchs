from django import forms


class AddStock(forms.Form):
    ticker = forms.CharField(required=True, label='ticker-input', max_length=200)
    company = forms.CharField(required=True, label='company-input', max_length=200)
    order_date = forms.DateField(required=True, label='date-input')
    number = forms.IntegerField(required=True, label='number-input')
    share_price = forms.FloatField(required=True, label='price-input')
