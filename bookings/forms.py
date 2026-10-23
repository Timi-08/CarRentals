from django import forms
from vehicles.models import Vehicle
from .models import Booking


class BookingForm(forms.ModelForm):
    """Customer picks vehicle, dates and location. Validation lives in
    Booking.clean() so the form and admin share the same rules."""

    class Meta:
        model = Booking
        fields = ['vehicle', 'pickup_date', 'return_date', 'location']
        widgets = {
            'pickup_date': forms.DateInput(attrs={'type': 'date'}),
            'return_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.filter(is_available=True)