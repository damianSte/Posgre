from django.core.management.base import BaseCommand
from myapp.models import Product, Customer, Order

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Delete any existing data
        Product.objects.all().delete()
        Customer.objects.all().delete()
        Order.objects.all().delete()

        # Create sample data
        product1 = Product.objects.create(name='Laptop', price=899.99, available=True)
        product2 = Product.objects.create(name='Headphones', price=199.99, available=True)
        product3 = Product.objects.create(name='Keyboard', price=49.99, available=True)

        customer1 = Customer.objects.create(name='Alice Smith', address='123 Apple St')
        customer2 = Customer.objects.create(name='Bob Brown', address='456 Orange Ave')

        order1 = Order.objects.create(customer=customer1, status='new')
        order1.products.add(product1, product2)

        order2 = Order.objects.create(customer=customer2, status='in_process')
        order2.products.add(product3)

        self.stdout.write("Sample data created successfully.")
