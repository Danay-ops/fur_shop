from decimal import Decimal

from django.core.paginator import Paginator
from django.shortcuts import render, get_list_or_404
from goods.models import Products,Categories

from goods.serializers import CategorySerializer, ProductSerializer, ProductGetterSerializer
from rest_framework.decorators import action

from rest_framework.response import Response
from rest_framework import viewsets



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

#GET /categories - возвращение списка категорий. У категорий может быть несколько уровней вложенности.
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for managing categories. It inherits from ReadOnlyModelViewSet,
    which provides read-only operations like 'list' and 'retrieve'.
    """
    serializer_class = CategorySerializer

    def get_queryset(self):
        
        return Categories.objects.all()
    
    
#POST /products — получение товаров по категории,
class ProductByCategoryApiView(viewsets.ViewSet):
    """
    A ViewSet for managing products by category. It inherits from ViewSet,
    which provides basic CRUD operations.

    The 'create' method is overridden to handle POST requests for retrieving products by category.
    """

    def create(self, request):
        """
        Handle POST requests to retrieve products by category.

        Parameters:
        - request (Request): The incoming request object containing the category slug in the request data.

        Returns:
        - Response: A JSON response containing the serialized products if the category is found.
                      If the category is not found, a JSON response with an error message and a 404 status code.
        """
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
        # Получение фильтров из URl
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

    # Тестовый метод для проверки фильтрации и сортировки
"""    @action(detail=False, methods=['get'])
    def test_filter_and_sort(self, request):
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        sort_by = request.query_params.get('sort_by', 'price')

        queryset = self.queryset

        # Фильтрация
        if min_price:
            queryset = queryset.filter(price__gte=Decimal(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=Decimal(max_price))

        # Сортировка
        if sort_by.startswith('-'):
            field_name = sort_by[1:]  # Получить имя поля для сортировки без минуса "-"
            queryset = queryset.order_by('-' + field_name)
        else:
            queryset = queryset.order_by(sort_by)

        # Преобразование в список для удобства вывода
        product_list = [
            {'id': product.id, 'name': product.name, 'price': product.price}
            for product in queryset
        ]
        return Response(product_list)"""



