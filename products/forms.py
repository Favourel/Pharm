from django import forms
from .models import Order, ProductReview
from django_recaptcha.fields import ReCaptchaField


class ReviewForm(forms.ModelForm):
    RATING_TYPES = (
        (1, "★☆☆☆☆ (1/5)"), (2, "★★☆☆☆ (2/5)"), (3, "★★★☆☆ (3/5)"),
        (4, "★★★★☆ (4/5)"), (5, "★★★★★ (5/5)")
    )

    rating = forms.CharField(widget=forms.Select(choices=RATING_TYPES, attrs={
        'class': 'u-form-group u-form-message',
        'name': 'rating',

    }))

    message = forms.CharField(widget=forms.Textarea(attrs={
        "name": "product review",
        "placeholder": "Product Review?",
        'type': 'text',
        "rows": 3,
        "cols": 50,
        "required": True,
        'class': 'u-form-group u-form-message',
    }))
    captcha = ReCaptchaField()

    class Meta:
        model = ProductReview
        fields = ["rating", "message"]


class CheckoutForm(forms.ModelForm):
    address = forms.CharField(max_length=500, required=True, widget=forms.TextInput(attrs={
        "name": "address",
        "placeholder": "Enter house / apartment number and street address",
        'type': 'text',
        "required": True,
        "id": "my-address"
    }))
    captcha = ReCaptchaField()

    class Meta:
        model = Order
        fields = ['address']
