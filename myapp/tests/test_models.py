
from django.test import TestCase
from myapp.models import Product, Customer, Order
from django.core.exceptions import ValidationError
from django.db import IntegrityError

class ProductModelTest(TestCase):
    def test_create_product_with_valid_data(self):
        temp_product = Product.objects.create(name='Temporary product',
        price=1.99, available=True)
        self.assertEqual(temp_product.name, 'Temporary product')
        self.assertEqual(temp_product.price, 1.99)
        self.assertTrue(temp_product.available)

    def test_create_product_with_negative_price(self):
        with self.assertRaises(ValidationError):
            temp_product = Product.objects.create(name='Invalid product', price=-1.99, available=True)
            temp_product.full_clean()

    def test_create_product_with_missing_price(self):
        with self.assertRaises(ValidationError):
            temp_product = Product(name='No Price Product', available=True)
            temp_product.full_clean()

    def test_create_product_with_missing_availability(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(name='No Availability', price=9.99)

    def test_create_product_with_blank_name(self):
        with self.assertRaises(ValidationError):
            temp_product = Product(name='', price=9.99, available=True)
            temp_product.full_clean()

    def test_create_product_with_min_length_name(self):
        temp_product = Product.objects.create(name='A', price=9.99, available=True)
        self.assertEqual(temp_product.name, 'A')

    def test_create_product_with_max_length_name(self):
        long_name = 'A' * 255
        temp_product = Product.objects.create(name=long_name, price=9.99, available=True)
        self.assertEqual(temp_product.name, long_name)

    def test_create_product_with_exceeding_max_length_name(self):
        long_name = 'A' * 255
        with self.assertRaises(ValidationError):
            temp_product = Product(name=long_name, price=9.99, available=True)
            temp_product.full_clean()

    def test_create_product_with_min_price(self):
        temp_product = Product.objects.create(name='Minimum Price Product', price=0.01, available=True)
        self.assertEqual(temp_product.price, 0.01)

    def test_create_product_with_max_price(self):
        max_price = 9999999.99  # Arbitrary high value for price
        temp_product = Product.objects.create(name='Max Price Product', price=max_price, available=True)
        self.assertEqual(temp_product.price, max_price)

    def test_create_product_with_invalid_price_format(self):
        with self.assertRaises(ValidationError):
            temp_product = Product(name='Invalid Price Format', price= 9.999, available=True)
            temp_product.full_clean()

    def test_create_product_with_non_numeric_price(self):
        with self.assertRaises(ValidationError):
            temp_product = Product(name='Non-Numeric Price', price='not_a_number', available=True)
            temp_product.full_clean()



class CustomerModelTest(TestCase):

    def test_create_customer_with_valid_data(self):
        temp_customer = Customer.objects.create(name='Temporary customer', address='123 Main St')
        self.assertEqual(temp_customer.name, 'Temporary customer')
        self.assertEqual(temp_customer.address, '123 Main St')

    def test_create_customer_with_missing_name(self):
        with self.assertRaises(IntegrityError):
            Customer.objects.create(name = None, address="123 Main St")

    def test_create_customer_with_missing_address(self):
        with self.assertRaises(IntegrityError):
            Customer.objects.create(name="John Doe", address=None)

    def test_create_customer_with_blank_name(self):
        with self.assertRaises(ValidationError):
            customer = Customer(name="", address="123 Main St")
            customer.full_clean()

    def test_create_customer_with_blank_address(self):
        with self.assertRaises(ValidationError):
            customer = Customer(name="John Doe", address="")
            customer.full_clean()

    def test_create_customer_with_min_length_name(self):
        customer = Customer.objects.create(name="A", address="123 Main St")
        self.assertEqual(customer.name, "A")

    def test_create_customer_with_max_length_name(self):
        max_length_name = "A" * 100
        customer = Customer.objects.create(name=max_length_name, address="123 Main St")
        self.assertEqual(customer.name, max_length_name)

    def test_create_customer_with_exceeding_max_length_name(self):
        exceeding_name = "A" * 101  # 101 characters long
        with self.assertRaises(ValidationError):
            customer = Customer(name=exceeding_name, address="123 Main St")
            customer.full_clean()


class OrderModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Customer", address="123 Test St")
        self.product1 = Product.objects.create(name="Product 1", price=10.99, available=True)
        self.product2 = Product.objects.create(name="Product 2", price=15.50, available=True)
        self.unavailable_product = Product.objects.create(name="Unavailable Product", price=5.00, available=False)

    def test_create_order_with_valid_data(self):
        order = Order.objects.create(customer=self.customer, status="new")
        order.products.add(self.product1, self.product2)
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.status, "new")
        self.assertEqual(order.products.count(), 2)

    def test_create_order_with_missing_customer(self):
        with self.assertRaises(IntegrityError):
            order = Order.objects.create(status="new")
            order.products.add(self.product1)

    def test_create_order_with_missing_status(self):
        order = Order(customer=self.customer)
        order.save()
        order.products.add(self.product1)
        order.full_clean()
        self.assertEqual(order.status, "new")

    def test_create_order_with_invalid_status(self):
        with self.assertRaises(ValidationError):
            order = Order(customer=self.customer, status="invalid_status")
            order.full_clean()

    def test_calculate_total_price_with_products(self):
        order = Order.objects.create(customer=self.customer, status="new")
        order.products.add(self.product1, self.product2)
        self.assertEqual(float(order.calculate_total_price()), 26.49)

    def test_calculate_total_price_with_no_products(self):
        order = Order.objects.create(customer=self.customer, status="new")
        self.assertEqual(order.calculate_total_price(), 0.0)

    def test_can_be_fulfilled_with_all_products_available(self):
        order = Order.objects.create(customer=self.customer, status="new")
        order.products.add(self.product1, self.product2)
        self.assertTrue(order.can_be_fulfilled())

    def test_can_be_fulfilled_with_unavailable_product(self):
        order = Order.objects.create(customer=self.customer, status="new")
        order.products.add(self.product1, self.unavailable_product)
        self.assertFalse(order.can_be_fulfilled())