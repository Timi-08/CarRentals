from django import forms

from .models import Contact, Subscriber


# Public contact form used on the Contact Us page.
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'email', 'message')
        widgets = {'message': forms.Textarea(attrs={'rows': 5})}


# Small form for adding a visitor to the mailing list.
class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ('email',)

    def clean_email(self):
        # Normalise and reject duplicate subscriptions before saving.
        email = self.cleaned_data['email'].strip().lower()
        if Subscriber.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email address is already subscribed.')
        return email
