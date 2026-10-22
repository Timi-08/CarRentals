from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BookingForm
from .models import Booking


@login_required  # BKG-01: guests are sent to the login page
def create_booking(request):
    initial = {}
    if request.GET.get('vehicle'):
        initial['vehicle'] = request.GET['vehicle']  # lets a car page link here

    form = BookingForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        booking = form.save(commit=False)
        booking.customer = request.user      # always the logged-in user
        booking.status = Booking.PENDING     # BKG-07
        booking.save()
        messages.success(request, "Booking submitted. Waiting for confirmation.")
        return redirect('bookings:confirmation', pk=booking.pk)
    return render(request, 'bookings/form.html', {'form': form})


@login_required
def booking_confirmation(request, pk):
    # customer=request.user stops users opening other people's bookings
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    return render(request, 'bookings/confirmation.html', {'booking': booking})


@login_required
def my_bookings(request):
    """BKG-10: a customer sees only their own bookings (paginated, NFR-04)."""
    qs = Booking.objects.filter(customer=request.user).select_related('vehicle')
    page_obj = Paginator(qs, 10).get_page(request.GET.get('page'))
    return render(request, 'bookings/my_bookings.html', {'bookings': page_obj})


@login_required
@require_POST
def cancel_booking(request, pk):
    """BKG-09 / BKG-12: customers cancel only their own Pending bookings."""
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    if booking.can_customer_cancel:
        booking.status = Booking.CANCELLED
        booking.save()
        messages.success(request, "Booking cancelled.")
    else:
        messages.error(request, "Only Pending bookings can be cancelled.")
    return redirect('bookings:my_bookings')


@staff_member_required(login_url='accounts:admin_login')
def manage_bookings(request):
    """BKG-11: admin sees all bookings, optionally filtered by status."""
    qs = Booking.objects.select_related('customer', 'vehicle')
    status = request.GET.get('status')
    if status in (Booking.PENDING, Booking.CONFIRMED, Booking.CANCELLED):
        qs = qs.filter(status=status)
    else:
        status = None
    page_obj = Paginator(qs, 10).get_page(request.GET.get('page'))
    return render(request, 'bookings/manage.html',
                  {'bookings': page_obj, 'current_status': status})


@staff_member_required(login_url='accounts:admin_login')
@require_POST
def admin_update_booking(request, pk, action):
    """BKG-08: admin confirms or cancels a Pending booking."""
    booking = get_object_or_404(Booking, pk=pk)
    if booking.status != Booking.PENDING:
        messages.error(request, "Only Pending bookings can be changed.")
    elif action == 'confirm':
        booking.status = Booking.CONFIRMED
        booking.save()
        messages.success(request, f"Booking #{booking.pk} confirmed.")
    elif action == 'cancel':
        booking.status = Booking.CANCELLED
        booking.save()
        messages.success(request, f"Booking #{booking.pk} cancelled.")
    return redirect('bookings:manage')