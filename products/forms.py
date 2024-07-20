from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    address = forms.CharField(max_length=500, required=True, widget=forms.TextInput(attrs={
        "name": "address",
        "placeholder": "Enter house / apartment number and street address",
        'type': 'text',
        "required": True,
        "id": "my-address"
    }))

    class Meta:
        model = Order
        fields = ['address']
