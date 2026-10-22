from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import ContactForm, SubscribeForm
from .models import ContactDetails, PageContent


def contact_us(request):
    """Contact Us page: FAST CARS details plus the message form."""
    initial = {}
    if request.user.is_authenticated:
        initial = {'name': request.user.get_full_name() or request.user.username,
                   'email': request.user.email}
    form = ContactForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Thank you for contacting us. We will get back to you soon.')
        return redirect('contact:contact_us')
    return render(request, 'contact/contact_us.html', {
        'form': form,
        'details': ContactDetails.load(),
    })


@require_POST
def subscribe(request):
    """Subscribe an email address. Used by a small form, e.g. in the footer."""
    form = SubscribeForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Thank you for subscribing!')
    else:
        error = next(iter(form.errors.get('email', [])), 'Please enter a valid email address.')
        messages.error(request, error)

    # Go back to the page the form was on, but never to another website.
    next_url = request.POST.get('next', '')
    if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(next_url)
    return redirect('home')


def page_detail(request, slug):
    """A static page whose text the admin edits (About Us and so on)."""
    page = get_object_or_404(PageContent, slug=slug)
    return render(request, 'contact/page.html', {'page': page})
