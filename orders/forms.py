from django import forms
from .models import Order, PickupPoint
from users.models import User


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['article', 'user', 'status', 'pickup_point', 'issue_date']
        widgets = {
            'issue_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(
            role__in=['client', 'admin']
        )
        self.fields['pickup_point'].queryset = PickupPoint.objects.all()

        # Если редактируем существующий заказ, артикул только для чтения
        if self.instance and self.instance.pk:
            self.fields['article'].widget.attrs['readonly'] = 'readonly'