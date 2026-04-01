from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from products.models import Product


def login_view(request):
    """Страница входа"""
    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('product_list')
        else:
            messages.error(request, 'Неверный логин или пароль')

    return render(request, 'auth/login.html')


def logout_view(request):
    """Выход из системы"""
    logout(request)
    return redirect('login')


def guest_view(request):
    """Просмотр товаров как гость"""
    products = Product.objects.all()
    return render(request, 'products/list.html', {'products': products, 'guest_mode': True})