from django import forms

from .models import Brand


class VehicleFilterForm(forms.Form):
    q = forms.CharField(required=False, label='Search')
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.none(), required=False, empty_label='All brands'
    )
    min_price = forms.DecimalField(required=False, min_value=0, label='Minimum price per day')
    max_price = forms.DecimalField(required=False, min_value=0, label='Maximum price per day')
    seats = forms.IntegerField(required=False, min_value=1)
    available = forms.ChoiceField(
        required=False,
        choices=(('', 'Any availability'), ('true', 'Available'), ('false', 'Unavailable')),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['brand'].queryset = Brand.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        minimum = cleaned_data.get('min_price')
        maximum = cleaned_data.get('max_price')
        if minimum is not None and maximum is not None and maximum < minimum:
            self.add_error('max_price', 'Maximum price must be at least the minimum price.')
        return cleaned_data
