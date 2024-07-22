from django.db import models
from datetime import datetime
import uuid
from django.urls import reverse
from django.conf import settings
from ckeditor.fields import RichTextField


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100, default="Select Category")
    date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.name

    @staticmethod
    def getAllCategory():
        return Category.objects.all()


class Product(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    price = models.FloatField(default=0)
    description = RichTextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(default='thumbnail-placeholder-500x334.jpg', upload_to='product_images')

    rating_count = models.FloatField(default=0)
    product_purchase = models.IntegerField(default=0)

    date_posted = models.DateTimeField(default=datetime.now)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_posted"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product-detail", kwargs={"pk": self.id})

    @staticmethod
    def getProductByFilter(category_name):
        if category_name:
            return Product.objects.filter(category__name=category_name)
        else:
            return Product.objects.all()

    def amount(self):
        total = self.price * self.product_purchase
        return total


class ProductReview(models.Model):
    RATING_TYPES = (
        (1, "★☆☆☆☆ (1/5)"), (2, "★★☆☆☆ (2/5)"), (3, "★★★☆☆ (3/5)"),
        (4, "★★★★☆ (4/5)"), (5, "★★★★★ (5/5)")
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField(choices=RATING_TYPES, null=True, blank=True)
    message = models.TextField()
    date_posted = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ["-date_posted"]

    def __str__(self):
        return f'{self.user} review'


class Checkout(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    complete = models.BooleanField(default=False, null=True, blank=True)
    date_posted = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ["-date_posted"]

    def __str__(self):
        return f'{self.quantity} of {self.product}'

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class Order(models.Model):
    ORDER_CATEGORIES = [
        ("Pending", "Pending"), ("Delivered", "Delivered"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=30)
    order_item = models.ManyToManyField(Checkout, related_name="order_item")

    default_order_item = models.CharField(max_length=1000, null=True, blank=True)
    default_price = models.FloatField(default=0)

    reference = models.CharField(max_length=500, null=True, blank=True)

    ordered = models.BooleanField(default=False)
    date_posted = models.DateTimeField(default=datetime.now)
    address = models.CharField(max_length=500, null=True, blank=True)
    order_status = models.CharField(choices=ORDER_CATEGORIES, max_length=50)

    class Meta:
        ordering = ["-date_posted"]

    def __str__(self):
        return f'{self.user}'

    def get_absolute_url(self):
        return reverse("order_summary", kwargs={"order_id": self.transaction_id})

    @property
    def total_order_item_price(self):
        total = self.order_item.all()
        total_price = sum([i.get_total for i in total])
        return total_price

