from rest_framework import serializers
from goods.models import Categories, Products

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    class Meta:
        model = Categories
        fields = ['id', 'name', 'slug', 'children']

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'

class ProductGetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'