from __future__ import annotations

from django.http import HttpRequest

from .cart import get_cart_manager_class

Cart = get_cart_manager_class()


def cart(request: HttpRequest) -> dict:
    return {"dj_shop_cart": Cart.new(request)}
