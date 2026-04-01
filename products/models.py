from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Manufacturer(models.Model):
    name = models.CharField(max_length=200, verbose_name='Производитель')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'


class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name='Поставщик')
    contact = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Контакты'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'


class Product(models.Model):
    UNIT_CHOICES = [
        ('шт', 'Штука'),
        ('пара', 'Пара'),
        ('компл', 'Комплект'),
    ]

    # Основные поля
    article = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Артикул'
    )
    name = models.CharField(max_length=200, verbose_name='Наименование')
    description = models.TextField(blank=True, verbose_name='Описание')

    # Связи
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        verbose_name='Производитель'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        verbose_name='Поставщик'
    )

    # Цены и количество
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена'
    )
    discount = models.IntegerField(default=0, verbose_name='Скидка (%)')
    quantity = models.IntegerField(
        default=0,
        verbose_name='Количество на складе'
    )
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default='шт',
        verbose_name='Ед. измерения'
    )

    # Изображение
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name='Фото'
    )

    def final_price(self):
        """Итоговая цена со скидкой"""
        return self.price * (100 - self.discount) / 100

    def is_in_stock(self):
        return self.quantity > 0

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'