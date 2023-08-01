from rest_framework import status
from django.contrib.auth.models import User
from model_bakery import baker
from store.models import Collection, Product
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post('/store/collections/', collection)
    return do_create_collection




@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anaynmose_return_401(self, create_collection):
        response = create_collection({"title": "wtf"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_return_403(self, create_collection, authenticate):
        authenticate()

        response = create_collection({"title": "wtf"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_return_400(self, create_collection, authenticate):
        authenticate(is_staff=True)

        response = create_collection({"title": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_data_is_valid_return_201(self, create_collection, authenticate):
        authenticate(is_staff=True)

        response = create_collection({"title": "wtf"})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestRetriveCollection:
    def test_if_collection_exists_returns_200(self, api_client):
        collection = baker.make(Collection)

        response = api_client.get(f"/store/collections/{collection.id}/")

        assert response.data == {
            'id': collection.id,
            'title': collection.title,
            'products_count': 0
        }

    def test_if_collection_does_not_exists_returns_404(self, api_client):

        response = api_client.get(f"/store/collections/{-1}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_collection_exists_returns_200(self, api_client):
        collection = baker.make(Collection)

        response = api_client.get(f"/store/collections/{collection.id}/")

        assert response.data == {
            'id': collection.id,
            'title': collection.title,
            'products_count': 0
        }


@pytest.mark.django_db
class TestDestroyCollection:
    def test_if_user_not_authenticated_returns_401(self, api_client):
        collection = baker.make(Collection)

        response = api_client.delete(f"/store/collections/{collection.id}/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] is not None

    def test_if_user_not_admin_returns_403(self, api_client, authenticate):
        collection = baker.make(Collection)
        authenticate()

        response = api_client.delete(f"/store/collections/{collection.id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] is not None

    def test_if_collection_does_not_exist_returns_404(self, api_client, authenticate):
        authenticate(is_staff=True)

        response = api_client.delete("/store/collections/0/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] is not None

    def test_if_collection_has_products_returns_405(self, authenticate, api_client: APIClient):
        collection = baker.make(Collection)
        baker.make(Product, collection=collection)
        authenticate(is_staff=True)

        response = api_client.delete(
            f"/store/collections/{collection.id}/")

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert response.data['error'] is not None


@pytest.mark.django_db
class TestUpdateCollection:

    def test_if_user_is_anonymous_return_401(self, api_client: APIClient):
        collection = baker.make(Collection)

        response = api_client.put(
            f"/store/collections/{collection.id}/", {'title': "test1"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_return_403(self, authenticate, api_client: APIClient):
        authenticate()
        collection = baker.make(Collection)

        response = api_client.put(
            f"/store/collections/{collection.id}/", {'title': "test1"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_collection_does_not_exist_return_404(self, authenticate, api_client: APIClient):
        authenticate(is_staff=True)

        response = api_client.put(
            "/store/collections/0/", {'title': "test1"})

        assert response.status_code == status.HTTP_404_NOT_FOUND

