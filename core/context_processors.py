"""
Global context processors — data available in every template.
"""
from .models import SiteLogo


def site_globals(request):
    """Inject logo and custom nav pages into every template context."""
    context = {}

    try:
        context['logo'] = SiteLogo.objects.last()
    except Exception:
        context['logo'] = None

    try:
        from .models import Page
        context['nav_custom_pages'] = Page.objects.filter(
            show_in_nav=True,
            is_published=True,
        ).order_by('nav_order')
    except Exception:
        context['nav_custom_pages'] = []

    return context
