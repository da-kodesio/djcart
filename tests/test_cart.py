from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.base import SessionBase
from django.test import RequestFactory

from cart.cart import get_cart_manager_class
from cart.storages import DBStorage, SessionStorage
from tests.factories import ProductFactory

pytestmark = pytest.mark.django_db

Cart = get_cart_manager_class()
User = get_user_model()


# TODO test with custom cart manager class
#   test with variants


def test_cart_init_session_storage(cart: Cart):
    assert isinstance(cart.storage, SessionStorage)
    assert len(cart) == cart.unique_count == cart.count == 0


def test_cart_init_db_storage(cart_db: Cart, settings):
    assert isinstance(cart_db.storage, DBStorage)
    assert len(cart_db) == cart_db.unique_count == cart_db.count == 0


def add_product_to_cart(cart: Cart):
    product = ProductFactory()
    cart.add(product, price=product.price, quantity=10)
    assert len(cart) == cart.unique_count == 1
    assert cart.count == 10
    assert cart.find_one(product=product).product == product
    assert product in cart.products


def test_cart_add_session_storage(cart: Cart):
    add_product_to_cart(cart=cart)


def test_cart_add_db_storage(cart_db: Cart):
    add_product_to_cart(cart=cart_db)


def add_product_multiple_to_cart(cart: Cart):
    product_a = ProductFactory()
    product_b = ProductFactory()
    cart.add(product_a, price=product_a.price, quantity=10)
    cart.add(product_b, price=product_b.price, quantity=5)
    cart.add(product_a, price=product_a.price, quantity=10)
    assert len(cart) == cart.unique_count == 2
    assert cart.count == 25
    assert product_a in cart.products
    assert product_a in cart.products
    assert cart.find_one(product=product_a).quantity == 20
    assert cart.find_one(product=product_b).quantity == 5


def test_cart_add_multiple_session_storage(cart: Cart):
    add_product_multiple_to_cart(cart=cart)


def test_cart_add_multiple_db_storage(cart_db: Cart):
    add_product_multiple_to_cart(cart=cart_db)


def add_product_override_quantity(cart: Cart):
    product = ProductFactory()
    cart.add(product, price=product.price, quantity=5)
    cart.add(product, price=product.price, quantity=5, override_quantity=True)
    assert len(cart) == cart.unique_count == 1
    assert cart.count == 5


def test_cart_add_override_quantity_session_storage(cart: Cart):
    add_product_override_quantity(cart=cart)


def test_cart_add_override_quantity_db_storage(cart_db: Cart):
    add_product_override_quantity(cart=cart_db)


def cart_is_empty(cart: Cart):
    assert cart.is_empty
    product = ProductFactory()
    cart.add(product, price=product.price, quantity=2)
    assert not cart.is_empty


def test_cart_is_empty_session_storage(cart: Cart):
    cart_is_empty(cart=cart)


def test_cart_is_empty_db_storage(cart_db):
    cart_is_empty(cart=cart_db)


def test_migrate_cart_from_session_to_db(
    cart: Cart, session: SessionBase, rf: RequestFactory, django_user_model: User
):
    request = rf.get("/")
    user = django_user_model.objects.create(username="someone", password="password")
    request.user = user
    request.session = session
    product = ProductFactory()
    cart.add(product, price=product.price, quantity=5)
    assert isinstance(cart.storage, SessionStorage)
    cart = Cart(request=request)
    assert isinstance(cart.storage, DBStorage)
    assert product in cart.products


def cart_remove_product(cart: Cart):
    product = ProductFactory()
    cart.remove(product, quantity=1)
    assert cart.is_empty
    cart.add(product, price=product.price, quantity=10)
    assert cart.count == 10
    cart.remove(product, quantity=2)
    assert cart.count == 8
    cart.remove(product)
    assert cart.is_empty


def test_cart_remove_session_storage(cart: Cart):
    cart_remove_product(cart)


def test_cart_remove_db_storage(cart_db: Cart):
    cart_remove_product(cart_db)


def empty_cart(cart: Cart):
    product = ProductFactory()
    cart.add(product, price=product.price, quantity=10)
    cart.empty()
    assert cart.is_empty
    assert len(cart) == cart.count == cart.unique_count == 0


def test_empty_cart_session_storage(cart: Cart):
    empty_cart(cart=cart)


def test_empty_cart_db_storage(cart_db: Cart):
    empty_cart(cart=cart_db)