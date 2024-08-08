from haystack import indexes
from products.models import Product


class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    # id = indexes.IntegerField(model_attr='id')
    name = indexes.CharField(model_attr="name")
    description = indexes.CharField(model_attr="description")
    price = indexes.IntegerField(model_attr="price")

    # large_numeric_field = indexes.CharField(model_attr='get_large_numeric_field_as_string')  # Convert to string

    content_auto = indexes.EdgeNgramField(model_attr="name")

    class Meta:
        model = Product
        fields = ["text", "id", "name", "description", "price",]

    def get_model(self):
        return Product

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
