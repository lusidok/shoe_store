from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .models import Product, Supplier
from .forms import ProductForm


def is_admin(user):
    return user.role == 'admin'


def is_manager_or_admin(user):
    return user.role in ['admin', 'manager']


def product_list(request):
    """Список товаров с фильтрацией, сортировкой и поиском"""
    products = Product.objects.select_related(
        'category', 'manufacturer', 'supplier'
    ).all()

    # Поиск по тексту (для менеджера и администратора)
    if request.user.is_authenticated and request.user.role in ['admin', 'manager']:
        search_query = request.GET.get('search', '')
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(manufacturer__name__icontains=search_query)
                | Q(supplier__name__icontains=search_query)
            )

        # Фильтр по поставщику
        supplier_id = request.GET.get('supplier')
        if supplier_id and supplier_id != 'all':
            products = products.filter(supplier_id=supplier_id)

        # Сортировка по количеству
        sort_order = request.GET.get('sort', '')
        if sort_order == 'quantity_asc':
            products = products.order_by('quantity')
        elif sort_order == 'quantity_desc':
            products = products.order_by('-quantity')

    # Получаем всех поставщиков для фильтра
    suppliers = Supplier.objects.all()

    # Сохраняем параметры для формы
    context = {
        'products': products,
        'suppliers': suppliers,
        'search_query': request.GET.get('search', ''),
        'selected_supplier': request.GET.get('supplier', 'all'),
        'sort_order': request.GET.get('sort', ''),
        'is_manager': request.user.is_authenticated
        and request.user.role == 'manager',
        'is_admin': request.user.is_authenticated
        and request.user.role == 'admin',
    }

    return render(request, 'products/list.html', context)


@login_required
@user_passes_test(is_admin)
def product_add(request):
    """Добавление товара (только администратор)"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(
        request,
        'products/product_form.html',
        {'form': form, 'title': 'Добавить товар'}
    )


@login_required
@user_passes_test(is_admin)
def product_edit(request, pk):
    """Редактирование товара (только администратор)"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # Если загружено новое фото, удаляем старое
            if 'image' in request.FILES and product.image:
                import os
                if os.path.isfile(product.image.path):
                    os.remove(product.image.path)
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        'products/product_form.html',
        {'form': form, 'title': 'Редактировать товар', 'product': product}
    )


@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    """Удаление товара (только администратор)"""
    product = get_object_or_404(Product, pk=pk)

    # Проверяем, есть ли товар в заказах
    if product.orderitem_set.exists():
        from django.contrib import messages
        messages.error(
            request,
            'Нельзя удалить товар, который присутствует в заказах!'
        )
        return redirect('product_list')

    if request.method == 'POST':
        # Удаляем фото
        if product.image:
            import os
            if os.path.isfile(product.image.path):
                os.remove(product.image.path)
        product.delete()
        return redirect('product_list')

    return render(
        request,
        'products/product_confirm_delete.html',
        {'product': product}
    )