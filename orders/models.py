from django.db import models
from django.conf import settings
from products.models import Product


class PickupPoint(models.Model):
    """Пункт выдачи заказов"""
    code = models.IntegerField(unique=True, verbose_name='Код пункта выдачи')
    address = models.CharField(max_length=500, verbose_name='Адрес')

    def __str__(self):
        return f"{self.code}: {self.address}"

    class Meta:
        verbose_name = 'Пункт выдачи'
        verbose_name_plural = 'Пункты выдачи'


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('ready', 'Готов к выдаче'),
        ('issued', 'Выдан'),
        ('cancelled', 'Отменен'),
    ]

    article = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Артикул заказа'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Клиент'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    pickup_point = models.ForeignKey(
        PickupPoint,
        on_delete=models.CASCADE,
        verbose_name='Пункт выдачи'
    )
    order_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата заказа'
    )
    issue_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата выдачи'
    )

    def __str__(self):
        return f"Заказ {self.article} - {self.user.full_name}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.IntegerField(default=1, verbose_name='Количество')
    price_at_time = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена на момент заказа'
    )

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'