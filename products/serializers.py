from rest_framework import serializers


class ProductSearchSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.IntegerField()
    description = serializers.CharField()
