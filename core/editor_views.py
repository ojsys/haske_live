import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.text import slugify
from .models import (
    Page, PageSection, PageSectionCard, BlogPost,
    HeroSlide, Statistics, Achievement, MinistrySection, Ministry, Gallery, SiteLogo,
    AboutPage, AboutMinistry, MissionVision, Challenge, BoardMember,
    ProjectPage, Project,
    VolunteerPage, GoTeam, PrayerPartner, GiveSection,
    MediaPage, YouTubeVideo, SpotifyPodcast,
    DonationPage, BankAccount,
)


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
    if 'show_header' in d:
        page.show_header = d['show_header'] == 'true'
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


# ---------------------------------------------------------------
#  Duplicate Page
# ---------------------------------------------------------------

@staff_required
@require_http_methods(['POST'])
def editor_duplicate_page(request, page_id):
    original = get_object_or_404(Page, id=page_id)

    # Create a unique slug
    base_slug = f"{original.slug}-copy"
    slug, n = base_slug, 1
    while Page.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{n}"
        n += 1

    new_page = Page.objects.create(
        title=f"{original.title} (Copy)",
        nav_label=original.nav_label,
        slug=slug,
        meta_description=original.meta_description,
        header_image=original.header_image,
        is_published=False,
        show_in_nav=False,
        nav_order=original.nav_order,
    )

    for section in original.sections.prefetch_related('cards').order_by('order'):
        new_section = PageSection.objects.create(
            page=new_page,
            section_type=section.section_type,
            order=section.order,
            title=section.title,
            subtitle=section.subtitle,
            body=section.body,
            image=section.image,
            image_position=section.image_position,
            button_text=section.button_text,
            button_url=section.button_url,
            button2_text=section.button2_text,
            button2_url=section.button2_url,
            background=section.background,
            css_class=section.css_class,
            is_visible=section.is_visible,
            extra_data=section.extra_data,
        )
        for card in section.cards.all():
            PageSectionCard.objects.create(
                section=new_section,
                icon=card.icon,
                image=card.image,
                title=card.title,
                body=card.body,
                link_text=card.link_text,
                link_url=card.link_url,
                order=card.order,
            )

    return JsonResponse({'id': new_page.id, 'title': new_page.title, 'slug': new_page.slug})


# ---------------------------------------------------------------
#  Blog editor
# ---------------------------------------------------------------

@staff_required
def editor_blog_list(request):
    posts = BlogPost.objects.order_by('-published_date')
    return render(request, 'editor/blog_list.html', {'posts': posts})


@staff_required
def editor_blog_edit(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    return render(request, 'editor/blog_editor.html', {'post': post})


@staff_required
def editor_blog_new(request):
    """Render the editor for a brand-new (unsaved) post."""
    return render(request, 'editor/blog_editor.html', {'post': None})


@staff_required
@require_http_methods(['POST'])
def editor_blog_save(request, post_id=None):
    """Create or update a blog post."""
    d = request.POST

    if post_id:
        post = get_object_or_404(BlogPost, id=post_id)
    else:
        post = BlogPost()

    post.title = d.get('title', post.title if post_id else 'New Post').strip() or 'New Post'
    post.author = d.get('author', post.author if post_id else '').strip()
    post.excerpt = d.get('excerpt', '').strip()
    post.content = d.get('content', '')
    post.is_featured = d.get('is_featured') == 'true'

    # Handle slug
    raw_slug = d.get('slug', '').strip()
    if raw_slug:
        candidate = slugify(raw_slug)
        if candidate and not BlogPost.objects.filter(slug=candidate).exclude(pk=post.pk).exists():
            post.slug = candidate
    elif not post_id:
        base = slugify(post.title)
        slug, n = base, 1
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base}-{n}"
            n += 1
        post.slug = slug

    if 'featured_image' in request.FILES:
        post.featured_image = request.FILES['featured_image']

    if request.user.is_authenticated:
        if not post_id:
            post.created_by = request.user
        post.last_modified_by = request.user

    post.save()
    return JsonResponse({
        'status': 'ok',
        'id': post.id,
        'slug': post.slug,
        'featured_image': post.featured_image.url if post.featured_image else '',
    })


@staff_required
@require_http_methods(['POST'])
def editor_blog_delete(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    post.delete()
    return JsonResponse({'status': 'ok'})


# ================================================================
#  SITE PAGE EDITORS  (existing hardcoded pages)
# ================================================================

# ---------------------------------------------------------------
#  Home
# ---------------------------------------------------------------

@staff_required
def editor_site_home(request):
    return render(request, 'editor/site_home.html', {
        'slides':           list(HeroSlide.objects.order_by('order')),
        'stats':            Statistics.objects.last(),
        'achievement':      Achievement.objects.first(),
        'logo':             SiteLogo.objects.last(),
        'ministry_section': MinistrySection.objects.first(),
        'ministries':       list(Ministry.objects.order_by('order')),
        'gallery_items':    list(Gallery.objects.order_by('-created_at')),
    })


@staff_required
@require_http_methods(['POST'])
def editor_hero_slide_add(request):
    last  = HeroSlide.objects.order_by('-order').first()
    order = (last.order + 1) if last else 0
    slide = HeroSlide.objects.create(title='New Slide', order=order)
    return JsonResponse({
        'id': slide.id, 'title': slide.title, 'subtitle': slide.subtitle,
        'description': slide.description, 'button_text': slide.button_text,
        'button_link': slide.button_link, 'order': slide.order,
        'is_active': slide.is_active, 'image_url': '',
    })


@staff_required
@require_http_methods(['POST'])
def editor_hero_slide_save(request, slide_id):
    slide = get_object_or_404(HeroSlide, id=slide_id)
    d = request.POST
    for f in ['title', 'subtitle', 'description', 'button_text', 'button_link']:
        if f in d:
            setattr(slide, f, d[f])
    if 'is_active' in d:
        slide.is_active = d['is_active'] == 'true'
    if 'order' in d:
        try:
            slide.order = int(d['order'])
        except ValueError:
            pass
    if 'image' in request.FILES:
        slide.image = request.FILES['image']
    slide.save()
    return JsonResponse({'status': 'ok', 'image_url': slide.image.url if slide.image else ''})


@staff_required
@require_http_methods(['POST'])
def editor_hero_slide_delete(request, slide_id):
    get_object_or_404(HeroSlide, id=slide_id).delete()
    return JsonResponse({'status': 'ok'})


@staff_required
@require_http_methods(['POST'])
def editor_stats_save(request):
    stats = Statistics.objects.last() or Statistics()
    d = request.POST
    for f in ['title', 'subtitle', 'stat_title1', 'stat_desc1', 'stat_title2', 'stat_desc2']:
        if f in d:
            setattr(stats, f, d[f])
    for f in ['total_population', 'people_groups', 'states', 'lgas', 'wards', 'villages',
              'converts', 'film_attendees', 'people_reached',
              'bible_translations', 'active_missionaries', 'training_sessions']:
        if f in d and d[f]:
            try:
                setattr(stats, f, int(d[f]))
            except ValueError:
                pass
    stats.save()
    return JsonResponse({'status': 'ok'})


@staff_required
@require_http_methods(['POST'])
def editor_achievement_save(request):
    ach = Achievement.objects.first() or Achievement()
    d = request.POST
    int_fields = [
        'villages', 'people_saved', 'people_reached', 'states_reached',
        'lgas_reached', 'wards_reached', 'people_discipled', 'people_baptized',
        'started_discipleship', 'bibles_shared', 'audiobibles_shared', 'sdcards_shared',
    ]
    text_fields = [
        'villages_description', 'people_saved_description', 'people_reached_description',
        'states_reached_description', 'lgas_reached_description', 'wards_reached_description',
        'people_discipled_description', 'people_baptized_description',
        'started_discipleship_description', 'bibles_shared_description',
        'audiobibles_description', 'sdcard_description',
    ]
    for f in int_fields:
        if f in d and d[f]:
            try:
                setattr(ach, f, int(d[f]))
            except ValueError:
                pass
    for f in text_fields:
        if f in d:
            setattr(ach, f, d[f])
    ach.save()
    return JsonResponse({'status': 'ok'})


@staff_required
@require_http_methods(['POST'])
def editor_ministry_section_save(request):
    ms = MinistrySection.objects.first() or MinistrySection()
    d = request.POST
    for f in ['title', 'description']:
        if f in d:
            setattr(ms, f, d[f])
    if 'image' in request.FILES:
        ms.image = request.FILES['image']
    ms.save()
    return JsonResponse({'status': 'ok', 'image_url': ms.image.url if ms.image else ''})


@staff_required
@require_http_methods(['POST'])
def editor_ministry_add(request):
    last  = Ministry.objects.order_by('-order').first()
    order = (last.order + 1) if last else 0
    ministry = Ministry.objects.create(title='New Ministry', description='', order=order)
    return JsonResponse({
        'id': ministry.id, 'title': ministry.title,
        'description': ministry.description, 'order': ministry.order, 'icon_url': '',
    })


@staff_required
@require_http_methods(['POST'])
def editor_ministry_save(request, ministry_id):
    ministry = get_object_or_404(Ministry, id=ministry_id)
    d = request.POST
    for f in ['title', 'description']:
        if f in d:
            setattr(ministry, f, d[f])
    if 'order' in d:
        try:
            ministry.order = int(d['order'])
        except ValueError:
            pass
    if 'icon' in request.FILES:
        ministry.icon = request.FILES['icon']
    ministry.save()
    return JsonResponse({'status': 'ok', 'icon_url': ministry.icon.url if ministry.icon else ''})


@staff_required
@require_http_methods(['POST'])
def editor_ministry_delete(request, ministry_id):
    get_object_or_404(Ministry, id=ministry_id).delete()
    return JsonResponse({'status': 'ok'})


@staff_required
@require_http_methods(['POST'])
def editor_gallery_add(request):
    item = Gallery.objects.create(title='New Image', description='', is_featured=False)
    return JsonResponse({
        'id': item.id, 'title': item.title,
        'description': item.description, 'is_featured': item.is_featured, 'image_url': '',
    })


@staff_required
@require_http_methods(['POST'])
def editor_gallery_save(request, gallery_id):
    item = get_object_or_404(Gallery, id=gallery_id)
    d = request.POST
    for f in ['title', 'description']:
        if f in d:
            setattr(item, f, d[f])
    if 'is_featured' in d:
        item.is_featured = d['is_featured'] == 'true'
    if 'image' in request.FILES:
        item.image = request.FILES['image']
    item.save()
    return JsonResponse({'status': 'ok', 'image_url': item.image.url if item.image else ''})


@staff_required
@require_http_methods(['POST'])
def editor_gallery_delete(request, gallery_id):
    get_object_or_404(Gallery, id=gallery_id).delete()
    return JsonResponse({'status': 'ok'})


# ---------------------------------------------------------------
#  About
# ---------------------------------------------------------------

@staff_required
def editor_site_about(request):
    return render(request, 'editor/site_about.html', {
        'about':          AboutPage.objects.first(),
        'mission_vision': MissionVision.objects.first(),
        'ministries':     list(AboutMinistry.objects.order_by('order')),
        'challenge':      Challenge.objects.first(),
        'board_members':  list(BoardMember.objects.order_by('order')),
    })


@staff_required
@require_http_methods(['POST'])
def editor_about_page_save(request):
    about = AboutPage.objects.first() or AboutPage()
    d = request.POST
    for f in ['title', 'banner_subtitle', 'introduction', 'ministry_goal', 'cta_heading', 'cta_body']:
        if f in d:
            setattr(about, f, d[f])
    if 'header_image' in request.FILES:
        about.header_image = request.FILES['header_image']
    about.save()
    return JsonResponse({'status': 'ok', 'image_url': about.header_image.url if about.header_image else ''})


@staff_required
@require_http_methods(['POST'])
def editor_mission_vision_save(request):
    mv = MissionVision.objects.first() or MissionVision()
    d = request.POST
    for f in ['mission_title', 'mission_text', 'vision_title', 'vision_text']:
        if f in d:
            setattr(mv, f, d[f])
    if 'mission_image' in request.FILES:
        mv.mission_image = request.FILES['mission_image']
    if 'vision_image' in request.FILES:
        mv.vision_image = request.FILES['vision_image']
    mv.save()
    return JsonResponse({'status': 'ok'})


@staff_required
@require_http_methods(['POST'])
def editor_board_member_add(request):
    last   = BoardMember.objects.order_by('-order').first()
    order  = (last.order + 1) if last else 0
    member = BoardMember.objects.create(name='New Member', position='', bio='', order=order)
    return JsonResponse({
        'id': member.id, 'name': member.name, 'position': member.position,
        'bio': member.bio, 'order': member.order, 'image_url': '',
    })


@staff_required
@require_http_methods(['POST'])
def editor_board_member_save(request, member_id):
    member = get_object_or_404(BoardMember, id=member_id)
    d = request.POST
    for f in ['name', 'position', 'bio']:
        if f in d:
            setattr(member, f, d[f])
    if 'order' in d:
        try:
            member.order = int(d['order'])
        except ValueError:
            pass
    if 'image' in request.FILES:
        member.image = request.FILES['image']
    member.save()
    return JsonResponse({'status': 'ok', 'image_url': member.image.url if member.image else ''})


@staff_required
@require_http_methods(['POST'])
def editor_board_member_delete(request, member_id):
    get_object_or_404(BoardMember, id=member_id).delete()
    return JsonResponse({'status': 'ok'})


# ---------------------------------------------------------------
#  About — Ministry pillars (AboutMinistry CRUD)
# ---------------------------------------------------------------

@staff_required
@require_http_methods(['POST'])
def editor_about_ministry_add(request):
    last  = AboutMinistry.objects.order_by('-order').first()
    order = (last.order + 1) if last else 0
    m = AboutMinistry.objects.create(title='New Ministry', description='', order=order)
    return JsonResponse({'id': m.id, 'title': m.title, 'order': m.order, 'image_url': ''})


@staff_required
@require_http_methods(['POST'])
def editor_about_ministry_save(request, ministry_id):
    m = get_object_or_404(AboutMinistry, id=ministry_id)
    d = request.POST
    for f in ['title', 'description']:
        if f in d:
            setattr(m, f, d[f])
    if 'order' in d:
        try:
            m.order = int(d['order'])
        except ValueError:
            pass
    if 'image' in request.FILES:
        m.image = request.FILES['image']
    m.save()
    return JsonResponse({'status': 'ok', 'image_url': m.image.url if m.image else ''})


@staff_required
@require_http_methods(['POST'])
def editor_about_ministry_delete(request, ministry_id):
    get_object_or_404(AboutMinistry, id=ministry_id).delete()
    return JsonResponse({'status': 'ok'})


# ---------------------------------------------------------------
#  About — The Challenges (singleton)
# ---------------------------------------------------------------

@staff_required
@require_http_methods(['POST'])
def editor_challenge_save(request):
    ch = Challenge.objects.first() or Challenge()
    d  = request.POST
    for f in ['title', 'description',
              'challenge1_title', 'challenge1_desc',
              'challenge2_title', 'challenge2_desc',
              'challenge3_title', 'challenge3_desc']:
        if f in d:
            setattr(ch, f, d[f])
    for img_f in ['challenge1_image', 'challenge2_image', 'challenge3_image']:
        if img_f in request.FILES:
            setattr(ch, img_f, request.FILES[img_f])
    ch.save()
    return JsonResponse({'status': 'ok'})


# ---------------------------------------------------------------
#  Projects
# ---------------------------------------------------------------

@staff_required
def editor_site_projects(request):
    return render(request, 'editor/site_projects.html', {
        'page':     ProjectPage.objects.first(),
        'projects': list(Project.objects.order_by('order')),
    })


@staff_required
@require_http_methods(['POST'])
def editor_projects_page_save(request):
    page = ProjectPage.objects.first() or ProjectPage()
    d = request.POST
    for f in ['title', 'introduction']:
        if f in d:
            setattr(page, f, d[f])
    if 'header_image' in request.FILES:
        page.header_image = request.FILES['header_image']
    page.save()
    return JsonResponse({'status': 'ok', 'image_url': page.header_image.url if page.header_image else ''})


@staff_required
@require_http_methods(['POST'])
def editor_project_add(request):
    last    = Project.objects.order_by('-order').first()
    order   = (last.order + 1) if last else 0
    project = Project.objects.create(title='New Project', description='', order=order)
    return JsonResponse({
        'id': project.id, 'title': project.title, 'description': project.description,
        'location': project.location or '', 'beneficiaries': project.beneficiaries,
        'order': project.order, 'image_url': '',
    })


@staff_required
@require_http_methods(['POST'])
def editor_project_save(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    d = request.POST
    for f in ['title', 'description', 'location']:
        if f in d:
            setattr(project, f, d[f])
    if 'beneficiaries' in d and d['beneficiaries']:
        try:
            project.beneficiaries = int(d['beneficiaries'])
        except ValueError:
            pass
    if 'date' in d and d['date']:
        try:
            from datetime import date
            project.date = date.fromisoformat(d['date'])
        except ValueError:
            pass
    if 'image' in request.FILES:
        project.image = request.FILES['image']
    project.save()
    return JsonResponse({'status': 'ok', 'image_url': project.image.url if project.image else ''})


@staff_required
@require_http_methods(['POST'])
def editor_project_delete(request, project_id):
    get_object_or_404(Project, id=project_id).delete()
    return JsonResponse({'status': 'ok'})


# ---------------------------------------------------------------
#  Volunteer
# ---------------------------------------------------------------

@staff_required
def editor_site_volunteer(request):
    return render(request, 'editor/site_volunteer.html', {
        'page':           VolunteerPage.objects.first(),
        'go_team':        GoTeam.objects.first(),
        'prayer_partner': PrayerPartner.objects.first(),
        'give_section':   GiveSection.objects.first(),
    })


@staff_required
@require_http_methods(['POST'])
def editor_site_volunteer_save(request):
    section = request.POST.get('section', 'page')
    d = request.POST

    if section == 'page':
        obj = VolunteerPage.objects.first() or VolunteerPage()
        for f in ['title', 'introduction']:
            if f in d:
                setattr(obj, f, d[f])
        if 'header_image' in request.FILES:
            obj.header_image = request.FILES['header_image']
        obj.save()
        return JsonResponse({'status': 'ok', 'image_url': obj.header_image.url if obj.header_image else ''})

    model_map = {'go_team': GoTeam, 'prayer_partner': PrayerPartner, 'give': GiveSection}
    ModelClass = model_map.get(section)
    if not ModelClass:
        return JsonResponse({'status': 'error', 'message': 'Invalid section'}, status=400)
    obj = ModelClass.objects.first() or ModelClass()
    for f in ['title', 'description']:
        if f in d:
            setattr(obj, f, d[f])
    if 'image' in request.FILES:
        obj.image = request.FILES['image']
    obj.save()
    return JsonResponse({'status': 'ok', 'image_url': obj.image.url if obj.image else ''})


# ---------------------------------------------------------------
#  Give / Donate
# ---------------------------------------------------------------

@staff_required
def editor_site_give(request):
    return render(request, 'editor/site_give.html', {
        'page':     DonationPage.objects.first(),
        'accounts': list(BankAccount.objects.all()),
    })


@staff_required
@require_http_methods(['POST'])
def editor_site_give_save(request):
    page = DonationPage.objects.first() or DonationPage()
    d = request.POST
    for f in ['title', 'description', 'bank_name']:
        if f in d:
            setattr(page, f, d[f])
    if 'header_image' in request.FILES:
        page.header_image = request.FILES['header_image']
    page.save()
    return JsonResponse({'status': 'ok', 'image_url': page.header_image.url if page.header_image else ''})


@staff_required
@require_http_methods(['POST'])
def editor_bank_account_add(request):
    account = BankAccount.objects.create()
    return JsonResponse({
        'id': account.id, 'bank_name': account.bank_name or '',
        'account_name': account.account_name or '',
        'account_number': account.account_number or '',
        'description': account.description or '',
    })


@staff_required
@require_http_methods(['POST'])
def editor_bank_account_save(request, account_id):
    account = get_object_or_404(BankAccount, id=account_id)
    d = request.POST
    for f in ['bank_name', 'account_name', 'account_number', 'description']:
        if f in d:
            setattr(account, f, d[f])
    account.save()
    return JsonResponse({'status': 'ok'})


@staff_required
@require_http_methods(['POST'])
def editor_bank_account_delete(request, account_id):
    get_object_or_404(BankAccount, id=account_id).delete()
    return JsonResponse({'status': 'ok'})


# ---------------------------------------------------------------
#  Media
# ---------------------------------------------------------------

@staff_required
def editor_site_media(request):
    return render(request, 'editor/site_media.html', {
        'page':     MediaPage.objects.first(),
        'videos':   list(YouTubeVideo.objects.order_by('-published_date')),
        'podcasts': list(SpotifyPodcast.objects.order_by('-published_date')),
    })


@staff_required
@require_http_methods(['POST'])
def editor_site_media_save(request):
    page = MediaPage.objects.first() or MediaPage()
    d = request.POST
    for f in ['title', 'blog_section_title', 'youtube_section_title', 'podcast_section_title']:
        if f in d:
            setattr(page, f, d[f])
    if 'header_image' in request.FILES:
        page.header_image = request.FILES['header_image']
    page.save()
    return JsonResponse({'status': 'ok'})


@staff_required
@require_http_methods(['POST'])
def editor_video_add(request):
    from django.utils import timezone
    video = YouTubeVideo.objects.create(
        title='New Video', description='', video_id='', published_date=timezone.now()
    )
    return JsonResponse({
        'id': video.id, 'title': video.title, 'description': video.description,
        'video_id': video.video_id, 'is_featured': video.is_featured,
        'published_date': video.published_date.strftime('%Y-%m-%d'),
    })


@staff_required
@require_http_methods(['POST'])
def editor_video_save(request, video_id):
    video = get_object_or_404(YouTubeVideo, id=video_id)
    d = request.POST
    for f in ['title', 'description', 'video_id']:
        if f in d:
            setattr(video, f, d[f])
    if 'is_featured' in d:
        video.is_featured = d['is_featured'] == 'true'
    if 'published_date' in d and d['published_date']:
        try:
            from datetime import datetime
            from django.utils import timezone as tz
            video.published_date = tz.make_aware(datetime.strptime(d['published_date'], '%Y-%m-%d'))
        except ValueError:
            pass
    video.save()
    return JsonResponse({'status': 'ok'})


@staff_required
@require_http_methods(['POST'])
def editor_video_delete(request, video_id):
    get_object_or_404(YouTubeVideo, id=video_id).delete()
    return JsonResponse({'status': 'ok'})


@staff_required
@require_http_methods(['POST'])
def editor_podcast_add(request):
    from django.utils import timezone
    podcast = SpotifyPodcast.objects.create(
        title='New Podcast', description='', spotify_id='',
        published_date=timezone.now(), duration='00:00',
    )
    return JsonResponse({
        'id': podcast.id, 'title': podcast.title, 'description': podcast.description,
        'spotify_id': podcast.spotify_id, 'duration': podcast.duration,
        'is_featured': podcast.is_featured,
        'published_date': podcast.published_date.strftime('%Y-%m-%d'),
    })


@staff_required
@require_http_methods(['POST'])
def editor_podcast_save(request, podcast_id):
    podcast = get_object_or_404(SpotifyPodcast, id=podcast_id)
    d = request.POST
    for f in ['title', 'description', 'spotify_id', 'duration']:
        if f in d:
            setattr(podcast, f, d[f])
    if 'is_featured' in d:
        podcast.is_featured = d['is_featured'] == 'true'
    if 'published_date' in d and d['published_date']:
        try:
            from datetime import datetime
            from django.utils import timezone as tz
            podcast.published_date = tz.make_aware(datetime.strptime(d['published_date'], '%Y-%m-%d'))
        except ValueError:
            pass
    podcast.save()
    return JsonResponse({'status': 'ok'})


@staff_required
@require_http_methods(['POST'])
def editor_podcast_delete(request, podcast_id):
    get_object_or_404(SpotifyPodcast, id=podcast_id).delete()
    return JsonResponse({'status': 'ok'})
