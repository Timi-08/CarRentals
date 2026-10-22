from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .forms import VehicleFilterForm
from .models import Vehicle


def vehicle_list(request):
    form = VehicleFilterForm(request.GET or None)
    vehicles = Vehicle.objects.select_related('brand')
    if form.is_valid():
        filters = form.cleaned_data
        if filters['q']:
            query = filters['q'].strip()
            vehicles = vehicles.filter(
                Q(name__icontains=query)
                | Q(brand__name__icontains=query)
                | Q(description__icontains=query)
            )
        if filters['brand']:
            vehicles = vehicles.filter(brand=filters['brand'])
        if filters['min_price'] is not None:
            vehicles = vehicles.filter(price_per_day__gte=filters['min_price'])
        if filters['max_price'] is not None:
            vehicles = vehicles.filter(price_per_day__lte=filters['max_price'])
        if filters['seats'] is not None:
            vehicles = vehicles.filter(seats=filters['seats'])
        if filters['available']:
            vehicles = vehicles.filter(available=filters['available'] == 'true')
    page_obj = Paginator(vehicles, 9).get_page(request.GET.get('page'))
    return render(
        request,
        'vehicles/vehicle_list.html',
        {'form': form, 'page_obj': page_obj},
    )


def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle.objects.select_related('brand'), pk=pk)
    return render(request, 'vehicles/vehicle_detail.html', {'vehicle': vehicle})
