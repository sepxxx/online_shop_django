
import datetime
from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import json
from . utils import *
# from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.

def prod(request):
    return render(request, 'store/prod.html')
@login_required(login_url='login')
def userOrders(request):
    # проверяем есть ли у юзера complete заказы
    orders_ids = Order.objects.filter(customer=request.user.customer, complete=True)
        # .values_list("id", flat=True)

    orders = {}
    for order_id in orders_ids:
        orders[order_id] = OrderItem.objects.filter(order=order_id)
    # print(orders)

    uauth = request.user.is_authenticated

    context = { 'orders': orders, 'uauth': uauth}

    return render(request, 'store/orders.html', context)

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + username)
                return redirect('login')

        context = {'form': form}
        return render(request, 'store/register.html', context)
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('store')
            else:
                messages.info(request, 'Username or pass is incorrect')
        context = {}
        return render(request, 'store/login.html')
def logoutUser(request):
    logout(request)
    return redirect('login')


def store(request):
    # if request.user.is_authenticated:
    #     customer = request.user.customer
    #     order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #     items = order.orderitem_set.all()
    # else:
    #     items = []
    #     order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    uauth = request.user.is_authenticated
    products = Product.objects.all()
    context = {'products': products, 'uauth': uauth}
    return render(request, 'store/store.html', context)
def cart(request):
    data = cartData(request)
    # cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    uauth = request.user.is_authenticated
    context = {'items': items, 'order': order, 'uauth': uauth}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    # cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    uauth = request.user.is_authenticated
    context = {'items': items, 'order': order, 'uauth': uauth}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print("Action:", action)
    print("productId:", productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action =='remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)


    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    # часть логики paypal оплаты будет на фронте
    # чтобы юзеры не могли подменить тотал здесь нужна проверка
    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],

        )

    return JsonResponse("Payment complete", safe=False)