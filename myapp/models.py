from django.core.exceptions import ValidationError, InvalidOperation
from django.db import models
from django.db.models.fields import DecimalField
from decimal import Decimal

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    address = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    available = models.BooleanField()

    def clean(self):
        super().clean()  # Call the parent class's clean method
        if self.price is not None:
            try:
                # Try to convert price to Decimal
                self.price = Decimal(self.price)
                if self.price < 0:
                    raise ValidationError("Price must be positive.")
            except (InvalidOperation, TypeError):
                raise ValidationError("Price must be a valid decimal number.")

    def __str__(self):
        return self.name


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product)
    date = models.DateTimeField(auto_now_add=True)  # Automatically set to now when created
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_process', 'In Process'),
        ('sent', 'Sent'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    def __str__(self):
        return f"Order {self.id} for {self.customer.name}"

    def calculate_total_price(self):
        return sum(product.price for product in self.products.all())

    def can_be_fulfilled(self):
        return all(product.available for product in self.products.all())
