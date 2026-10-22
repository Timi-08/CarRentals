from django.shortcuts import render

from contact.models import SiteContent
from vehicles.models import Vehicle


def home(request):
    return render(
        request,
        'home.html',
        {
            'site_content': SiteContent.get_solo(),
            'featured_vehicles': Vehicle.objects.filter(
                featured=True, available=True
            ).select_related('brand')[:3],
        },
    )
