from django import forms
from .models import Product, Category, Manufacturer, Supplier


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'article', 'name', 'description', 'category', 'manufacturer',
            'supplier', 'price', 'discount', 'quantity', 'unit', 'image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'discount': forms.NumberInput(attrs={'min': '0', 'max': '100'}),
            'quantity': forms.NumberInput(attrs={'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['manufacturer'].queryset = Manufacturer.objects.all()
        self.fields['supplier'].queryset = Supplier.objects.all()