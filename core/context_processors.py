"""
Global context processors — data available in every template.
"""
from .models import SiteLogo


def site_globals(request):
    """Inject logo, custom nav pages, and admin-bar data into every template context."""
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

    # Footer — settings, link columns and social icons
    try:
        from .models import FooterSettings, FooterLink, FooterSocial
        # Fall back to an unsaved instance so the template still renders the
        # model defaults before an admin has ever saved the footer.
        context['footer'] = FooterSettings.objects.first() or FooterSettings()
        links = FooterLink.objects.filter(is_active=True)
        context['footer_quick_links'] = [l for l in links if l.column == 'quick']
        context['footer_involved_links'] = [l for l in links if l.column == 'involved']
        context['footer_socials'] = FooterSocial.objects.filter(is_active=True)
    except Exception:
        context['footer'] = None
        context['footer_quick_links'] = []
        context['footer_involved_links'] = []
        context['footer_socials'] = []

    # Admin bar: detect if the current path is a custom page so we can link to its editor
    if request.user.is_active and request.user.is_staff:
        context['show_admin_bar'] = True
        # Try to find a custom page matching the current path
        path = request.path  # e.g. /pages/some-slug/
        context['admin_bar_edit_url'] = None
        context['admin_bar_page_id'] = None
        try:
            from .models import Page
            if path.startswith('/pages/'):
                slug = path.strip('/').split('/')[-1]
                page = Page.objects.filter(slug=slug).first()
                if page:
                    context['admin_bar_edit_url'] = f'/editor/page/{page.id}/'
                    context['admin_bar_page_id'] = page.id
        except Exception:
            pass
    else:
        context['show_admin_bar'] = False

    return context
