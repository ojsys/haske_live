import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.text import slugify
from .models import Page, PageSection, PageSectionCard


def _is_staff(user):
    return user.is_active and user.is_staff


def staff_required(view_fn):
    return login_required(user_passes_test(_is_staff, login_url='/admin/login/')(view_fn))


# ---------------------------------------------------------------
#  Dashboard
# ---------------------------------------------------------------

@staff_required
def editor_dashboard(request):
    pages = Page.objects.all().order_by('-updated_at')
    return render(request, 'editor/dashboard.html', {'pages': pages})


# ---------------------------------------------------------------
#  Page editor
# ---------------------------------------------------------------

@staff_required
def editor_page_view(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    sections = page.sections.prefetch_related('cards').order_by('order')

    sections_data = [_section_to_dict(s) for s in sections]

    return render(request, 'editor/page_editor.html', {
        'page': page,
        'sections_json': json.dumps(sections_data),
        'section_types': PageSection.SECTION_TYPES,
        'background_choices': PageSection.BACKGROUND_CHOICES,
        'image_positions': PageSection.IMAGE_POSITION,
        'page_header_image': page.header_image.url if page.header_image else '',
    })


# ---------------------------------------------------------------
#  Page CRUD
# ---------------------------------------------------------------

@staff_required
@require_http_methods(['POST'])
def editor_create_page(request):
    title = request.POST.get('title', 'New Page').strip() or 'New Page'
    slug = slugify(title)
    base, n = slug, 1
    while Page.objects.filter(slug=slug).exists():
        slug = f"{base}-{n}"
        n += 1
    page = Page.objects.create(title=title, slug=slug)
    return JsonResponse({'id': page.id, 'title': page.title, 'slug': page.slug})


@staff_required
@require_http_methods(['POST'])
def editor_save_page(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    d = request.POST

    if 'title' in d:
        page.title = d['title']
    if 'nav_label' in d:
        page.nav_label = d['nav_label']
    if 'slug' in d and d['slug'].strip():
        candidate = slugify(d['slug'])
        if candidate and not Page.objects.filter(slug=candidate).exclude(pk=page.pk).exists():
            page.slug = candidate
    if 'meta_description' in d:
        page.meta_description = d['meta_description']
    if 'is_published' in d:
        page.is_published = d['is_published'] == 'true'
    if 'show_in_nav' in d:
        page.show_in_nav = d['show_in_nav'] == 'true'
    if 'nav_order' in d:
        try:
            page.nav_order = int(d['nav_order'])
        except ValueError:
            pass
    if 'header_image' in request.FILES:
        page.header_image = request.FILES['header_image']

    page.save()
    return JsonResponse({
        'status': 'ok',
        'slug': page.slug,
        'header_image': page.header_image.url if page.header_image else '',
    })


@staff_required
@require_http_methods(['POST'])
def editor_delete_page(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    page.delete()
    return JsonResponse({'status': 'ok'})


# ---------------------------------------------------------------
#  Section CRUD
# ---------------------------------------------------------------

@staff_required
@require_http_methods(['POST'])
def editor_add_section(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    section_type = request.POST.get('section_type', 'text')
    last = page.sections.order_by('-order').first()
    order = (last.order + 1) if last else 0
    label = dict(PageSection.SECTION_TYPES).get(section_type, 'Section')
    section = PageSection.objects.create(
        page=page,
        section_type=section_type,
        order=order,
        title=f"New {label}",
    )
    return JsonResponse(_section_to_dict(section))


@staff_required
@require_http_methods(['POST'])
def editor_save_section(request, section_id):
    section = get_object_or_404(PageSection, id=section_id)
    d = request.POST

    text_fields = [
        'title', 'subtitle', 'body', 'section_type', 'background',
        'css_class', 'button_text', 'button_url', 'button2_text',
        'button2_url', 'image_position', 'extra_data',
    ]
    for f in text_fields:
        if f in d:
            setattr(section, f, d[f])

    if 'is_visible' in d:
        section.is_visible = d['is_visible'] == 'true'
    if 'image' in request.FILES:
        section.image = request.FILES['image']
    if d.get('remove_image') == 'true' and section.image:
        section.image.delete(save=False)
        section.image = None

    section.save()
    return JsonResponse({
        'status': 'ok',
        'image_url': section.image.url if section.image else '',
    })


@staff_required
@require_http_methods(['POST'])
def editor_delete_section(request, section_id):
    section = get_object_or_404(PageSection, id=section_id)
    section.delete()
    return JsonResponse({'status': 'ok'})


@staff_required
@require_http_methods(['POST'])
def editor_reorder_sections(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    try:
        items = json.loads(request.body)
        for item in items:
            PageSection.objects.filter(id=item['id'], page=page).update(order=item['order'])
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@staff_required
@require_http_methods(['POST'])
def editor_toggle_visibility(request, section_id):
    section = get_object_or_404(PageSection, id=section_id)
    section.is_visible = not section.is_visible
    section.save()
    return JsonResponse({'status': 'ok', 'is_visible': section.is_visible})


# ---------------------------------------------------------------
#  Card CRUD
# ---------------------------------------------------------------

@staff_required
@require_http_methods(['POST'])
def editor_add_card(request, section_id):
    section = get_object_or_404(PageSection, id=section_id)
    last = section.cards.order_by('-order').first()
    order = (last.order + 1) if last else 0
    card = PageSectionCard.objects.create(section=section, title='New Card', order=order)
    return JsonResponse(_card_to_dict(card))


@staff_required
@require_http_methods(['POST'])
def editor_save_card(request, card_id):
    card = get_object_or_404(PageSectionCard, id=card_id)
    d = request.POST
    for f in ['title', 'body', 'icon', 'link_text', 'link_url']:
        if f in d:
            setattr(card, f, d[f])
    if 'image' in request.FILES:
        card.image = request.FILES['image']
    card.save()
    return JsonResponse({
        'status': 'ok',
        'image_url': card.image.url if card.image else '',
    })


@staff_required
@require_http_methods(['POST'])
def editor_delete_card(request, card_id):
    card = get_object_or_404(PageSectionCard, id=card_id)
    card.delete()
    return JsonResponse({'status': 'ok'})


# ---------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------

def _section_to_dict(s):
    return {
        'id': s.id,
        'section_type': s.section_type,
        'section_type_display': s.get_section_type_display(),
        'order': s.order,
        'title': s.title,
        'subtitle': s.subtitle,
        'body': s.body,
        'background': s.background,
        'css_class': s.css_class,
        'button_text': s.button_text,
        'button_url': s.button_url,
        'button2_text': s.button2_text,
        'button2_url': s.button2_url,
        'image_url': s.image.url if s.image else '',
        'image_position': s.image_position,
        'extra_data': s.extra_data,
        'is_visible': s.is_visible,
        'cards': [_card_to_dict(c) for c in s.cards.all()],
    }


def _card_to_dict(c):
    return {
        'id': c.id,
        'title': c.title,
        'body': c.body,
        'icon': c.icon,
        'link_text': c.link_text,
        'link_url': c.link_url,
        'image_url': c.image.url if c.image else '',
        'order': c.order,
    }
