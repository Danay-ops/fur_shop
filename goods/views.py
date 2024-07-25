from decimal import Decimal

from django.core.paginator import Paginator
from django.shortcuts import render, get_list_or_404
from goods.models import Products,Categories
from rest_framework import viewsets
from goods.serializers import CategorySerializer, ProductSerializer,ProductGetterSerializer
from rest_framework.decorators import action
from rest_framework.response import Response



def catalog(request, category_slug):
    page = request.GET.get('page',1)

    if category_slug =='all':
        goods = Products.objects.all()
    else:
        goods = get_list_or_404( Products.objects.filter(category__slug=category_slug))

    paginator = Paginator(goods,3)
    current_page = paginator.page(int(page))
    context = {
        'goods' : current_page,
        'slug_url' : category_slug
    }
    return render(request,'goods/catalog.html', context)

def product(request, product_slug):
    product = Products.objects.get(slug=product_slug)
    context = {
        'product' : product
    }
    return render(request,'goods/product.html', context=context)



#-----------------------API------------------------------

# GET /categories
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Categories.objects.all()

class ProductByCategoryApiView(viewsets.ViewSet):
    def create(self, request):
        category_slug = request.data.get('category')
        category = Categories.objects.get(slug=category_slug)

        if category:
            category_id = category.id
            products = Products.objects.filter(category_id=category_id)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'Категория не найдена'}, status=404)




class ProductViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductGetterSerializer

    @action(detail=False, methods=['get'])
    def get_products(self, request):
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        sort_by = request.query_params.get('sort_by', 'price')

        queryset = self.queryset

        if min_price:
            queryset = queryset.filter(price__gte=Decimal(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=Decimal(max_price))

        if sort_by.startswith('-'):
            field_name = sort_by[1:]  # Получить имя поля для сортировки без минуса "-"
            queryset = queryset.order_by('-' + field_name)
        else:
            queryset = queryset.order_by(sort_by)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)



