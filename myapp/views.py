from django.shortcuts import render, get_object_or_404

# Create your views here.

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product
from decimal import Decimal



def hello_world(request):
    return HttpResponse("Hello World")


@csrf_exempt
def product_list(request):

    if request.method == 'GET':
        products = list(Product.objects.values('id', 'name', 'price', 'available'))
        return JsonResponse(products, safe=False)

    elif request.method == 'POST':

        try:
            data = json.loads(request.body)
            name = data.get('name')
            price = data.get('price')
            available = data.get('available')

            if not name or price is None or available is None:
                return HttpResponseBadRequest("Missing required fields in request body")

            product = Product(name=name, price=Decimal(str(price)), available=available)
            product.full_clean()
            product.save()

            return JsonResponse({'id': product.id, 'name': product.name, 'price': float(product.price), 'available': product.available},
                                status=201,
                                )

        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")

    else:
        return HttpResponseBadRequest("Method not allowed for this endpoint")



@csrf_exempt
def product_detail(request, product_id):

    try:
        product = get_object_or_404(Product, id=product_id)

        if request.method == 'GET':
            product = Product.objects.get(id=product_id)
            return JsonResponse({'id': product.id, 'name': product.name, 'price': float(product.price), 'available': product.available})

        else:
            return HttpResponseBadRequest("Method not allowed for this endpoint")


    except Product.DoesNotExist:
        return HttpResponseNotFound("Product not found")
