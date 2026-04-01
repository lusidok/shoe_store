import os
import django
import pandas as pd

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Импорты после настройки Django
from django.contrib.auth.hashers import make_password
from users.models import User
from products.models import Category, Manufacturer, Supplier, Product
from orders.models import Order, OrderItem, PickupPoint

DATA_DIR = 'data'


def import_users():
    """Импорт пользователей"""
    file_path = os.path.join(DATA_DIR, 'user_import.xlsx')
    if not os.path.exists(file_path):
        print("Ошибка: user_import.xlsx не найден")
        return

    df = pd.read_excel(file_path)
    role_map = {'Администратор': 'admin', 'Менеджер': 'manager', 'Клиент': 'client'}

    for _, row in df.iterrows():
        role = role_map.get(row['Роль сотрудника'], 'client')
        User.objects.get_or_create(
            username=row['Логин'],
            defaults={
                'full_name': row['ФИО'],
                'password': make_password(row['Пароль']),
                'role': role,
                'is_staff': role == 'admin',
                'is_superuser': role == 'admin',
            }
        )


def import_pickup_points():
    """Импорт пунктов выдачи"""
    file_path = os.path.join(DATA_DIR, 'Пункты выдачи.xlsx')
    if not os.path.exists(file_path):
        print("Ошибка: файл с пунктами выдачи не найден")
        return

    df = pd.read_excel(file_path, header=None)
    print(f"Импорт пунктов выдачи: {len(df)} записей")

    for idx, row in df.iterrows():
        code = idx + 1
        address = str(row[0]).strip()
        PickupPoint.objects.get_or_create(
            code=code,
            defaults={'address': address}
        )


def import_products():
    """Импорт товаров"""
    file_path = os.path.join(DATA_DIR, 'Tovar.xlsx')
    if not os.path.exists(file_path):
        print("Ошибка: Tovar.xlsx не найден")
        return

    df = pd.read_excel(file_path)

    # Создаем справочники
    for cat_name in df['Категория товара'].dropna().unique():
        Category.objects.get_or_create(name=cat_name.strip())

    for man_name in df['Производитель'].dropna().unique():
        Manufacturer.objects.get_or_create(name=man_name.strip())

    for sup_name in df['Поставщик'].dropna().unique():
        Supplier.objects.get_or_create(name=sup_name.strip())

    # Импортируем товары
    for _, row in df.iterrows():
        category = Category.objects.get(name=row['Категория товара'].strip())
        manufacturer = Manufacturer.objects.get(name=row['Производитель'].strip())
        supplier = Supplier.objects.get(name=row['Поставщик'].strip())

        # Фото в media/products/
        photo_path = f"products/{row['Фото']}" if pd.notna(row['Фото']) else None

        Product.objects.get_or_create(
            article=row['Артикул'],
            defaults={
                'name': row['Наименование товара'],
                'description': row['Описание товара'] if pd.notna(
                    row['Описание товара']
                ) else '',
                'category': category,
                'manufacturer': manufacturer,
                'supplier': supplier,
                'price': float(row['Цена']),
                'discount': int(row['Действующая скидка']) if pd.notna(
                    row['Действующая скидка']
                ) else 0,
                'quantity': int(row['Кол-во на складе']) if pd.notna(
                    row['Кол-во на складе']
                ) else 0,
                'unit': row['Единица измерения'] if pd.notna(
                    row['Единица измерения']
                ) else 'шт',
                'image': photo_path,
            }
        )


def import_orders():
    """Импорт заказов"""
    file_path = os.path.join(DATA_DIR, 'Заказ_import.xlsx')
    if not os.path.exists(file_path):
        print("Ошибка: Заказ_import.xlsx не найден")
        return

    df = pd.read_excel(file_path)

    for _, row in df.iterrows():
        # Ищем пользователя по ФИО
        try:
            user = User.objects.get(full_name=row['ФИО авторизированного клиента'])
        except User.DoesNotExist:
            continue

        # Ищем пункт выдачи по коду
        try:
            pickup_code = int(row['Адрес пункта выдачи'])
            pickup_point = PickupPoint.objects.get(code=pickup_code)
        except (ValueError, PickupPoint.DoesNotExist):
            continue

        # Формируем артикул заказа
        order_article = row['Артикул заказа'].split(',')[0] if ',' in str(
            row['Артикул заказа']
        ) else row['Артикул заказа']

        # Создаем заказ
        order, created = Order.objects.get_or_create(
            article=order_article,
            defaults={
                'user': user,
                'status': row['Статус заказа'],
                'pickup_point': pickup_point,
                'order_date': row['Дата заказа'],
                'issue_date': row['Дата доставки'] if pd.notna(
                    row['Дата доставки']
                ) else None,
            }
        )

        # Создаем позиции заказа
        items_str = str(row['Артикул заказа'])
        parts = items_str.split(', ')

        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                article = parts[i].strip()
                quantity = int(parts[i + 1].strip())

                try:
                    product = Product.objects.get(article=article)
                    OrderItem.objects.get_or_create(
                        order=order,
                        product=product,
                        defaults={
                            'quantity': quantity,
                            'price_at_time': product.price
                        }
                    )
                except Product.DoesNotExist:
                    pass


if __name__ == '__main__':
    print("Импорт данных...")

    import_users()
    import_pickup_points()
    import_products()
    import_orders()

    print("Done.")