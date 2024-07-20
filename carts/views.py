from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from goods.models import Products
from carts.models import Cart

from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import CartSerializer
from .utils import get_user_carts

"""def cart_add(request, product_slug):
    product = Products.objects.get(slug=product_slug)
    if request.user.is_authenticated:
        carts = Cart.objects.filter(user = request.user, product=product)
        if carts.exists():
            cart = carts.first()
            if cart:
                cart.quantity+=1
                cart.save()
        else:
            Cart.objects.create(user=request.user, product=product,quantity = 1)
    else:
        carts = Cart.objects.filter(
            session_key = request.session.session_key, product=product)
        if carts.exists():
            cart = carts.first()
            if cart:
                cart.quantity+=1
                cart.save()
        else:
            Cart.objects.create(session_key = request.session.session_key, product=product, quantity = 1)
    return redirect(request.META['HTTP_REFERER'])"""


def cart_add(request, product_slug):

    product = Products.objects.get(slug=product_slug)

    if request.user.is_authenticated:
        carts = Cart.objects.filter(user=request.user, product=product)

        if carts.exists():
            cart = carts.first()
            if cart:
                cart.quantity += 1
                cart.save()
        else:
            Cart.objects.create(user=request.user, product=product, quantity=1)
    user_cart = get_user_carts(request)
    return redirect(request.META['HTTP_REFERER'])

"""    else:
        carts = Cart.objects.filter(
            session_key=request.session.session_key, product=product)

        if carts.exists():
            cart = carts.first()
            if cart:
                cart.quantity += 1
                cart.save()
        else:
            Cart.objects.create(
                session_key=request.session.session_key, product=product, quantity=1)"""

"""    user_cart = get_user_carts(request)
    cart_items_html = render_to_string(
        "carts/includes/included_cart.html", {"carts": user_cart}, request=request)

    response_data = {
        "message": "Товар добавлен в корзину",
        "cart_items_html": cart_items_html,
    }

    return JsonResponse(response_data)"""


def cart_change(request,product_slug):
    cart_id = request.POST.get("cart_id")
    quantity = request.POST.get("quantity")

    cart = Cart.objects.get(id=cart_id)

    cart.quantity = quantity
    cart.save()
    updated_quantity = cart.quantity

    user_cart = get_user_carts(request)

    context = {"carts": user_cart}

    # if referer page is create_order add key orders: True to context
    referer = request.META.get('HTTP_REFERER')
    if reverse('orders:create_order') in referer:
        context["order"] = True

    cart_items_html = render_to_string(
        "carts/includes/included_cart.html", context, request=request)

    response_data = {
        "message": "Количество изменено",
        "cart_items_html": cart_items_html,
        "quantity": updated_quantity,
    }

    return JsonResponse(response_data)


def cart_remove(request,cart_id):
    cart = Cart.objects.get(id=cart_id)

    cart.delete()

    return redirect(request.META['HTTP_REFERER'])


#_________________________ API ________________________


class CartListCreateView(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = self.queryset.filter(user=request.user)  # Фильтруем корзины по текущему пользователю
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        product_slug = request.data.get('product_slug')
        product = Products.objects.get(slug=product_slug)
        user = request.user
        if user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=user, product=product)
            if created:
                cart.quantity = 1
            else:
                cart.quantity += 1
            cart.save()
            serializer = self.serializer_class(cart)
            return Response(serializer.data)
        else:
                pass


    def update(self, request, pk=None):
        cart = self.queryset.filter(user=request.user, id=pk).first()
        if not cart:
            return Response({'message': 'Корзина не найдена'}, status=404)

        # Логика обновления корзины

        serializer = self.serializer_class(cart)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        cart = self.queryset.filter(user=request.user, id=pk).first()
        if not cart:
            return Response({'message': 'Корзина не найдена'}, status=404)

        cart.delete()
        return Response(status=204)


