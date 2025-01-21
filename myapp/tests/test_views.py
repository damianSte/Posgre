from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from myapp.models import Product, Customer, Order
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken


class ProductApiTest(APITestCase):
    def setUp(self):
        # Create a test product
        self.product = Product.objects.create(name="Temporary Product", price=1.99, available=True)

        # URLs for CRUD operations
        self.product_list_url = reverse("product-list")
        self.product_detail_url = reverse("product-detail", kwargs={"pk": self.product.id})

        # Create test users
        self.regular_user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin = User.objects.create_superuser(username='testadmin', password='testpassword')

        # Client setup
        self.client = APIClient()

        # Generate and set a token for the regular user (default for most tests)
        self.token = str(AccessToken.for_user(self.regular_user))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_get_all_products(self):
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Temporary Product")
        self.assertEqual(response.data[0]["price"], "1.99")
        self.assertTrue(response.data[0]["available"])

    def test_get_all_products_as_regular_user(self):
        self.token = str(AccessToken.for_user(self.regular_user))
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product_as_admin(self):
        admin_token = str(AccessToken.for_user(self.admin))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        data = {"name": "Admin Created Product", "price": 5.99, "available": True}
        response = self.client.post(self.product_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_single_product(self):
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Temporary Product")
        self.assertEqual(response.data["price"], "1.99")
        self.assertTrue(response.data["available"])

    def test_create_product_as_regular_user(self):
        self.token = str(AccessToken.for_user(self.regular_user))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {"name": "Unauthorized Product", "price": 5.99, "available": True}
        response = self.client.post(self.product_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_modify_product(self):
        admin_token = str(AccessToken.for_user(self.admin))
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        data = {"name": "Modified Product"}
        response = self.client.patch(self.product_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Modified Product")
        self.assertEqual(response.data["price"], "1.99")
        self.assertTrue(response.data["available"])

    def test_delete_product(self):
        admin_token = str(AccessToken.for_user(self.admin))
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_unauthorized_access(self):
        # Ensure no credentials are set
        self.client.credentials()
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_access_without_token(self):
        # Ensure no credentials are set
        self.client.credentials()
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_product_invalid_price(self):
        data = {"name": "Invalid Product", "price": "invalid", "available": True}
        response = self.client.post(self.product_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_endpoint(self):
        invalid_url = "/api/invalid-endpoint/"
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_access_without_token(self):
        self.client.credentials()
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_action_as_regular_user(self):
        self.token = str(AccessToken.for_user(self.regular_user))
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_action_as_regular_user_modify(self):
        self.token = str(AccessToken.for_user(self.regular_user))
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        data = {"name": "Modified Product"}
        response = self.client.patch(self.product_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalidtoken")
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_product_as_unauthenticated_user(self):
        self.client.credentials()
        data = {"name": "New Product", "price": 5.99, "available": True}
        response = self.client.post(self.product_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_product_with_invalid_data(self):
        self.token = str(AccessToken.for_user(self.regular_user))
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        data = {"name": "New Product", "price": "invalid price", "available": True}
        response = self.client.patch(self.product_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
