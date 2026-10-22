from django import forms
from django.db.models import Q

from .models import Brand


class VehicleFilterForm(forms.Form):
    """Search and filter form for the car listing (submitted with GET)."""
    q = forms.CharField(required=False, label='Search',
                        widget=forms.TextInput(attrs={'placeholder': 'Name or brand'}))
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(), required=False, empty_label='All brands')
    min_price = forms.DecimalField(required=False, min_value=0, decimal_places=2,
                                   label='Min price per day')
    max_price = forms.DecimalField(required=False, min_value=0, decimal_places=2,
                                   label='Max price per day')
    seats = forms.IntegerField(required=False, min_value=1, label='Seats (at least)')
    available_only = forms.BooleanField(required=False, label='Available only')

    def clean(self):
        cleaned = super().clean()
        low, high = cleaned.get('min_price'), cleaned.get('max_price')
        if low is not None and high is not None and low > high:
            raise forms.ValidationError('Minimum price cannot be higher than maximum price.')
        return cleaned

    def filter(self, queryset):
        """Apply the (already validated) filters to a Vehicle queryset."""
        data = self.cleaned_data
        if data.get('q'):
            term = data['q'].strip()
            queryset = queryset.filter(Q(name__icontains=term) | Q(brand__name__icontains=term))
        if data.get('brand'):
            queryset = queryset.filter(brand=data['brand'])
        if data.get('min_price') is not None:
            queryset = queryset.filter(price_per_day__gte=data['min_price'])
        if data.get('max_price') is not None:
            queryset = queryset.filter(price_per_day__lte=data['max_price'])
        if data.get('seats'):
            queryset = queryset.filter(seats__gte=data['seats'])
        if data.get('available_only'):
            queryset = queryset.filter(is_available=True)
        return queryset
