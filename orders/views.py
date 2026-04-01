from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import models
from .models import Order
from .forms import OrderForm


def is_admin(user):
    return user.role == 'admin'


def is_manager_or_admin(user):
    return user.role in ['admin', 'manager']


@login_required
@user_passes_test(is_manager_or_admin)
def order_list(request):
    """Список заказов"""
    orders = Order.objects.select_related(
        'user', 'pickup_point'
    ).all().order_by('-order_date')

    # Фильтр по статусу
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            models.Q(article__icontains=search_query)
            | models.Q(user__full_name__icontains=search_query)
        )

    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': Order.STATUS_CHOICES,
        'is_admin': request.user.role == 'admin',
    }
    return render(request, 'orders/list.html', context)


@login_required
@user_passes_test(is_admin)
def order_add(request):
    """Добавление заказа (только администратор)"""
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            messages.success(
                request,
                f'Заказ {order.article} успешно создан!'
            )
            return redirect('order_list')
    else:
        form = OrderForm()

    return render(
        request,
        'orders/order_form.html',
        {'form': form, 'title': 'Добавить заказ'}
    )


@login_required
@user_passes_test(is_admin)
def order_edit(request, pk):
    """Редактирование заказа (только администратор)"""
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Заказ {order.article} успешно обновлен!'
            )
            return redirect('order_list')
    else:
        form = OrderForm(instance=order)

    return render(
        request,
        'orders/order_form.html',
        {'form': form, 'title': 'Редактировать заказ', 'order': order}
    )


@login_required
@user_passes_test(is_admin)
def order_delete(request, pk):
    """Удаление заказа (только администратор)"""
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        order.delete()
        messages.success(
            request,
            f'Заказ {order.article} успешно удален!'
        )
        return redirect('order_list')

    return render(
        request,
        'orders/order_confirm_delete.html',
        {'order': order}
    )