import uuid
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from orders.forms import CreateOrderForm
from goods.models import Products
from carts.models import Cart
from orders.models import Order
from rest_framework.exceptions import ValidationError
from django.conf import settings
from orders.models import OrderItem

#API
from rest_framework.views import APIView
from rest_framework import viewsets

from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from orders.serializers import OrderSerializer

from yookassa import Configuration, Payment




Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

"""@login_required
def create_order(request):
     if request.method == 'POST':
         form = CreateOrderForm(data=request.POST)
         if form.is_valid():
             try:
                 with transaction.atomic():
                     user = request.user
                     cart_items = Cart.objects.filter(user=user)

                     if cart_items.exists():
                         # Создать заказ
                         order = Order.objects.create(
                             user=user,
                             phone_number=form.cleaned_data['phone_number'],
                             requires_delivery=form.cleaned_data['requires_delivery'],
                             delivery_address=form.cleaned_data['delivery_address'],
                             payment_on_get=form.cleaned_data['payment_on_get'],
                        )
                         # Создать заказанные товары
                         for cart_item in cart_items:
                             product=cart_item.product
                             name=cart_item.product.name
                             price=cart_item.product.sell_price()
                             quantity=cart_item.quantity


                             if product.quantity < quantity:
                                 raise ValidationError(f'Недостаточное количество товара {name} на складе\
                                                        В наличии - {product.quantity}')

                             OrderItem.objects.create(
                                 order=order,
                                 product=product,
                                 name=name,
                                 price=price,
                                 quantity=quantity,
                             )
                             product.quantity -= quantity
                             product.save()

                         # Очистить корзину пользователя после создания заказа
                         cart_items.delete()

                         return redirect('user:profile')
             except ValidationError as e:

                 return redirect('orders:create_order')


     else:

         initial = {
             'first_name': request.user.first_name,
             'last_name': request.user.last_name,
             }

         form = CreateOrderForm(initial=initial)

     context = {
         'title': 'Home - Оформление заказа',
         'form': form,
         'order': True,
     }
     return render(request, 'orders/create_order.html', context=context)"""


@login_required
def create_order(request):
    if request.method == 'POST':
        payment_type = request.POST.get('stripe-payment', 'yookassa-payment')
        form = CreateOrderForm(request.POST)
        if form.is_valid():

            user = request.user
            cart_items = Cart.objects.filter(user=user)

            # Проверяем количество товаров в наличии
            for cart_item in cart_items:
                product = cart_item.product
                quantity = cart_item.quantity
                if product.quantity < quantity:
                    form.add_error(None, f'Недостаточное количество товара {product.name} на складе. В наличии - {product.quantity}')
                    return render(request, 'orders/create_order.html', {'form': form})

            # Получаем данные пользователя и доставки из формы

            phone_number = form.cleaned_data['phone_number']
            requires_delivery = form.cleaned_data['requires_delivery']
            delivery_address = form.cleaned_data['delivery_address']
            payment_on_get = form.cleaned_data['payment_on_get']

            # Создаем заказ
            order = Order.objects.create(
                user=user,
                phone_number=phone_number,
                requires_delivery=requires_delivery,
                delivery_address=delivery_address,
                payment_on_get=payment_on_get,
            )

            # Обрабатываем оплату через YooKassa
            payment_type = request.POST.get('yookassa-payment')
            if payment_type == 'yookassa-payment':
                idempotency_key = str(uuid.uuid4())
                currency = 'RUB'
                description = 'Товары в корзине'
                total_price = sum(cart_item.product.sell_price() *  cart_item.quantity for cart_item in cart_items)

                payment = Payment.create({
                    "amount": {
                        "value": str(total_price),
                        "currency": currency
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": request.build_absolute_uri(reverse('orders:payment-success')),
                    },
                    "capture": True,
                    "test": True,
                    "description": description,
                }, idempotency_key)

                confirmation_url = payment.confirmation.confirmation_url
                return redirect(confirmation_url)

            # Создаем записи о товарах в заказе
            for cart_item in cart_items:
                product = cart_item.product
                name = cart_item.product.name
                price = cart_item.product.sell_price()
                quantity = cart_item.quantity

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    name=name,
                    price=price,
                    quantity=quantity,
                )
                product.quantity -= quantity

            # После успешного создания заказа, очищаем корзину пользователя
            cart_items.delete()

            return redirect('orders:order-detail', order.id)

        else:
            return render(request, 'orders/create_order.html', {'form': form})

    else:
        form = CreateOrderForm()
        return render(request, 'orders/create_order.html', {'form': form})

def payment_success(request):
    for key in list(request.session.keys()):
         del request.session[key]
    return render(request, 'orders/payment-success.html')



#----------------------------- API -----------------------------



class CreateOrderView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    def post(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)


        if not cart_items.exists():
            return Response({"error": "Ваша корзина пуста"}, status=status.HTTP_400_BAD_REQUEST)

        form = CreateOrderForm(data=request.data)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Создать заказ
                    order = Order.objects.create(
                        user=user,
                        phone_number=form.cleaned_data['phone_number'],
                        requires_delivery=form.cleaned_data['requires_delivery'],
                        delivery_address=form.cleaned_data['delivery_address'],
                        payment_on_get=form.cleaned_data['payment_on_get'],
                    )

                    # Создать заказанные товары
                    for cart_item in cart_items:
                        product = cart_item.product
                        name = cart_item.product.name
                        price = cart_item.product.sell_price()
                        quantity = cart_item.quantity

                        if product.quantity < quantity:
                            raise ValueError(f'Недостаточное количество товара {name} на складе. В наличии - {product.quantity}')

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            name=name,
                            price=price,
                            quantity=quantity,
                        )
                        product.quantity -= quantity
                        product.save()

                    # Очистить корзину пользователя после создания заказа
                    cart_items.delete()

                    # Сериализовать заказ
                    order_serializer = OrderSerializer(order)
                    return Response(order_serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)