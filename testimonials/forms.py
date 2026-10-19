from django import forms
from .models import Testimonial


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['message']
        widgets = {'message': forms.Textarea(attrs={'rows': 4})}