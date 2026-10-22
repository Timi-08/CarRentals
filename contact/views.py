from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import ContactForm, SubscriberForm
from .models import SiteContent


def contact(request):
    content = SiteContent.get_solo()
    data = request.POST if request.method == 'POST' else None
    form = ContactForm(data)
    if request.user.is_authenticated and request.method == 'GET':
        form.initial.update(
            {'name': request.user.get_full_name(), 'email': request.user.email}
        )
    if request.method == 'POST' and form.is_valid():
        message = form.save(commit=False)
        if request.user.is_authenticated:
            message.user = request.user
        message.save()
        messages.success(request, 'Thank you. Your message has been sent.')
        return redirect('contact:contact')
    return render(
        request,
        'contact/contact.html',
        {'form': form, 'subscriber_form': SubscriberForm(), 'site_content': content},
    )


@require_POST
def subscribe(request):
    form = SubscriberForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'You have been added to the mailing list.')
        return redirect('contact:contact')
    return render(
        request,
        'contact/contact.html',
        {
            'form': ContactForm(),
            'subscriber_form': form,
            'site_content': SiteContent.get_solo(),
        },
    )
