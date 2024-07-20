from django import template
from carts.models import Cart

from carts.utils import get_user_carts

register = template.Library()
@register.simple_tag()
def user_carts(request):  # Получаю все корзины конкретного пользователя
    return get_user_carts(request)
