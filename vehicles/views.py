from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .forms import VehicleFilterForm
from .models import Vehicle

VEHICLES_PER_PAGE = 9
FEATURED_ON_HOME = 6


# Only show the short, highlighted set that the admin has marked as featured.
def featured_vehicles():
    """Available vehicles the admin marked as featured (used by the home page)."""
    return (Vehicle.objects.filter(is_featured=True, is_available=True)
            .select_related('brand')[:FEATURED_ON_HOME])


def home(request):
    """Home page: Daniel's home.html plus the featured-car data."""
    return render(request, 'home.html', {'featured_vehicles': featured_vehicles()})


def car_list(request):
    """Paginated car listing with search and filters, open to guests and users."""
    form = VehicleFilterForm(request.GET or None)
    vehicles = Vehicle.objects.select_related('brand')
    if form.is_valid():
        # Apply any user-selected filters before paging the result set.
        vehicles = form.filter(vehicles)
    page_obj = Paginator(vehicles, VEHICLES_PER_PAGE).get_page(request.GET.get('page'))

    # Keep the active filters in the pagination links.
    params = request.GET.copy()
    params.pop('page', None)
    return render(request, 'vehicles/car_list.html', {
        'form': form,
        'page_obj': page_obj,
        'querystring': params.urlencode(),
    })


def car_detail(request, pk):
    # Fetch one vehicle with its brand data so the detail template can display full information.
    vehicle = get_object_or_404(Vehicle.objects.select_related('brand'), pk=pk)
    return render(request, 'vehicles/car_detail.html', {'vehicle': vehicle})
