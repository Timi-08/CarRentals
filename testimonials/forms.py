from django import forms
from .models import Testimonial


# Form customers use to submit a review for admin approval.
class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['message']
        widgets = {'message': forms.Textarea(attrs={'rows': 4})}