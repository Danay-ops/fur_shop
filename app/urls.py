

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
#API
from rest_framework import routers
from goods.views import CategoryViewSet, ProductByCategoryApiView,ProductViewSet
from carts.views import CartListCreateView
from orders.views import CreateOrderView


router = routers.DefaultRouter()
#GET /categories - возвращение списка категорий. У категорий может быть несколько уровней вложенности.
router.register(r'api/category', CategoryViewSet, basename='category')
#POST /products — получение товаров по категории,
router.register(r'api/productsbycategory', ProductByCategoryApiView, basename='productsbycategory')
#GET, POST, PUT, DELETE  /cart
router.register(r'api/docarts', CartListCreateView, basename='docarts'),
#GET, POST, PUT, DELETE  /cart — для получения, добавления, изменения и удаления товаров в корзине, пользователь может получить только свою корзину,
router.register(r'api/products', ProductViewSet, basename='products')
#POST /order— создание заказа. Заказ должен сохранится в бд. После вызова эндпоинта корзина должна быть очищена.
router.register(r'api/createorders', CreateOrderView, basename='createorders')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls', namespace='main')),
    path('catalog/', include('goods.urls', namespace='catalog')),
    path('user/', include('users.urls', namespace='user')),
    path('cart/', include('carts.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),

    #API
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


