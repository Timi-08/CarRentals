from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from .forms import TestimonialForm
from .models import Testimonial


def testimonial_list(request):
    """Anyone can view active testimonials only (TST-02), paginated (NFR-04)."""
    qs = Testimonial.objects.filter(is_active=True).select_related('user')
    page_obj = Paginator(qs, 6).get_page(request.GET.get('page'))
    return render(request, 'testimonials/list.html', {'testimonials': page_obj})


@login_required
def testimonial_create(request):
    """Logged-in customers post a testimonial (TST-01). Guests go to login."""
    form = TestimonialForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        t = form.save(commit=False)
        t.user = request.user
        t.save()
        messages.success(request, "Thanks! Your testimonial will appear once approved.")
        return redirect('testimonials:list')
    return render(request, 'testimonials/form.html', {'form': form})