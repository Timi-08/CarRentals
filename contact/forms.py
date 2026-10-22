from django import forms

from .models import Contact, Subscriber


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'email', 'subject', 'message')
        widgets = {'message': forms.Textarea(attrs={'rows': 6})}


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if Subscriber.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already subscribed.')
        return email
