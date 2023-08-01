import pytest
from store.models import Product
from model_bakery import baker
from rest_framework import status


@pytest.fixture
def create_product(api_client):
    def do_create_product(product):
        return api_client.post('/store/products/', product)
    return do_create_product


@pytest.fixture
def delete_product(api_client):
    def do_delete_product(product_id):
        return api_client.delete(f'/store/products/{product_id}/')
    return do_delete_product


@pytest.mark.django_db
class TestCreateProduct:
    def test_if_user_is_anonymous_returns_401(self, create_product):
        product = baker.make(Product)

        response = create_product(product={
            "title": product.title,
            "slug": product.slug,
            "inventory": product.inventory,
            "unit_price": product.unit_price,
            "collection": product.collection.id
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, create_product, authenticate):
        authenticate()
        product = baker.make(Product)

        response = create_product(product={
            "title": product.title,
            "slug": product.slug,
            "inventory": product.inventory,
            "unit_price": product.unit_price,
            "collection": product.collection.id
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] is not None

    def test_if_data_is_invalid_return_400(self, create_product, authenticate):
        authenticate(is_staff=True)
        product = baker.make(Product)

        response = create_product(product={
            "slug": product.slug,
            "inventory": product.inventory,
            "unit_price": product.unit_price,
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_data_is_valid_returns_201(self, create_product, authenticate):
        product = baker.make(Product)
        product.unit_price = 10
        product.inventory = 10

        print("PRODUCT TITLE ", product.title)
        print("PRODUCT SLUG ", product.slug)
        print("PRODUCT inventory ", product.inventory)
        print("PRODUCT unit_price ", product.unit_price)
        print("PRODUCT collection ", product.collection.id)
        authenticate(is_staff=True)
        response = create_product({
            "title": product.title,
            "slug": product.slug,
            "inventory": product.inventory,
            "unit_price": product.unit_price,
            "collection": product.collection.id
        })
        print(" REQUEST DATA : ", response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestProductUpdate:
    def test_if_user_is_anoynomus_return_401(self, create_product):
        product = baker.make(Product)

        response = create_product(product={
            "title": product.title,
            "slug": product.slug,
            "inventory": product.inventory,
            "unit_price": product.unit_price,
            "collection": product.collection.id
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] is not None

    def test_if_user_is_not_admin_return_403(self, create_product, authenticate):
        product = baker.make(Product)
        authenticate()

        response = create_product(product={
            "title": product.title,
            "slug": product.slug,
            "inventory": product.inventory,
            "unit_price": product.unit_price,
            "collection": product.collection.id
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] is not None

    def test_if_data_is_invalid_return_400(self, create_product, api_client, authenticate):
        product = baker.make(Product)
        authenticate(is_staff=True)

        response = create_product(product={
            "title": product.title,
            "slug": product.slug,
            "inventory": product.inventory,
            "unit_price": product.unit_price,
            "collection": product.collection.id
        })

        response = api_client.put(f"/store/products/{product.id}/", {
            'collection': 0
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['collection'] is not None

    def test_if_data_is_valid_return_200(self, create_product, api_client, authenticate):
        product = baker.make(Product)
        authenticate(is_staff=True)

        response = create_product(product={
            "title": product.title,
            "slug": product.slug,
            "inventory": product.inventory,
            "unit_price": product.unit_price,
            "collection": product.collection.id
        })

        response = api_client.put(f"/store/products/{product.id}/", {

            "title": product.title,
            "slug": product.slug,
            "inventory": 10,
            "unit_price": product.unit_price,
            "collection": product.collection.id

        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestProductDelete:
    def test_if_user_is_anonymous_returns_401(self, create_product, delete_product):
        product = baker.make(Product)

        create_product(product={
            "title": product.title,
            "slug": product.slug,
            "inventory": product.inventory,
            "unit_price": product.unit_price,
            "collection": product.collection.id
        })

        response = delete_product(product.id)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] is not None

    def test_if_user_is_not_admin_returns_401(self, authenticate, create_product, delete_product):
        product = baker.make(Product)

        authenticate()

        create_product(product={
            "title": product.title,
            "slug": product.slug,
            "inventory": product.inventory,
            "unit_price": product.unit_price,
            "collection": product.collection.id
        })

        response = delete_product(product.id)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] is not None

    def test_if_product_does_not_exist_returns_404(self, authenticate, delete_product):

        authenticate(is_staff=True)

        response = delete_product(product_id=0)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] is not None

    def test_delete_product_returns_204(self, authenticate, create_product, delete_product):
        product = baker.make(Product)

        authenticate(is_staff=True)

        create_product(product={
            "title": product.title,
            "slug": product.slug,
            "inventory": product.inventory,
            "unit_price": product.unit_price,
            "collection": product.collection.id
        })

        response = delete_product(product.id)

        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestRetreiveProduct:
    def test_if_product_does_not_exist_returns_404(self, api_client):

        response = api_client.get("/store/products/-1/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_product_exist_returns_200(self, create_product, api_client):
        product = baker.make(Product)

        response = api_client.get(f"/store/products/{product.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] > 0
