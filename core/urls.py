from django.urls import path, include, re_path
from django.conf import settings
from .views import StateDemographicView, DemographicsMapView
from django.conf.urls.static import static
from django.views.static import serve
from . import views
from . import editor_views

urlpatterns = [
    path('', views.home, name='home'),
    # about
    path('about/', views.about, name='about'),
    # projects
    path('projects/', views.projects, name='projects'),
    # volunteers
    path('volunteer/', views.volunteer, name='volunteer'),
    # volunteers Apply
    path('volunteer/apply/', views.volunteer_apply, name='volunteer-apply'),
    # media
    path('media/', views.media_center, name='media'),
    # contact
    path('contact/', views.contact, name='contact'),
    
     # Report_test
    path('Report_test/', views.about, name='Report_test'),
    
    # give
    path('give/', views.give, name='give'),

    path('blog/', views.blog_list, name='blog-list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog-detail'),

    path('api/demographics/<str:state_name>/', StateDemographicView.as_view(), name='state-demographics'),
    path('demographics-map/', DemographicsMapView.as_view(), name='demographics-map'),
    path('api/state-data/', views.get_state_data, name='state-data'),
    path('api/state-data/<str:state_name>/', views.get_state_detail, name='state-detail'),
    # getting states with data
    path('api/states-with-data/', views.states_with_data, name='states_with_data'),
     
    path('state/<str:state_name>/', views.state_detail, name='state_detail'),
    # Subscribe
    path('subscribe/', views.subscribe, name='subscribe'),
    path('map/', views.map_view, name='map'),
    
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    # Custom page builder — must be last to avoid route conflicts
    path('pages/<slug:slug>/', views.custom_page, name='custom_page'),

    # ---- Frontend Page Editor ----
    path('editor/', editor_views.editor_dashboard, name='editor_dashboard'),
    path('editor/page/<int:page_id>/', editor_views.editor_page_view, name='editor_page'),

    # Page API
    path('editor/api/pages/create/', editor_views.editor_create_page, name='editor_create_page'),
    path('editor/api/pages/<int:page_id>/save/', editor_views.editor_save_page, name='editor_save_page'),
    path('editor/api/pages/<int:page_id>/delete/', editor_views.editor_delete_page, name='editor_delete_page'),
    path('editor/api/pages/<int:page_id>/reorder/', editor_views.editor_reorder_sections, name='editor_reorder_sections'),

    # Section API
    path('editor/api/pages/<int:page_id>/sections/add/', editor_views.editor_add_section, name='editor_add_section'),
    path('editor/api/sections/<int:section_id>/save/', editor_views.editor_save_section, name='editor_save_section'),
    path('editor/api/sections/<int:section_id>/delete/', editor_views.editor_delete_section, name='editor_delete_section'),
    path('editor/api/sections/<int:section_id>/toggle/', editor_views.editor_toggle_visibility, name='editor_toggle_visibility'),

    # Card API
    path('editor/api/sections/<int:section_id>/cards/add/', editor_views.editor_add_card, name='editor_add_card'),
    path('editor/api/cards/<int:card_id>/save/', editor_views.editor_save_card, name='editor_save_card'),
    path('editor/api/cards/<int:card_id>/delete/', editor_views.editor_delete_card, name='editor_delete_card'),

    # Duplicate Page API
    path('editor/api/pages/<int:page_id>/duplicate/', editor_views.editor_duplicate_page, name='editor_duplicate_page'),

    # ---- Site Page Editors (existing pages) ----
    path('editor/site/home/',      editor_views.editor_site_home,      name='editor_site_home'),
    path('editor/site/about/',     editor_views.editor_site_about,     name='editor_site_about'),
    path('editor/site/projects/',  editor_views.editor_site_projects,  name='editor_site_projects'),
    path('editor/site/volunteer/', editor_views.editor_site_volunteer, name='editor_site_volunteer'),
    path('editor/site/give/',      editor_views.editor_site_give,      name='editor_site_give'),
    path('editor/site/media/',     editor_views.editor_site_media,     name='editor_site_media'),

    # Hero Slides
    path('editor/api/site/hero/add/',                  editor_views.editor_hero_slide_add,    name='editor_hero_slide_add'),
    path('editor/api/site/hero/<int:slide_id>/save/',   editor_views.editor_hero_slide_save,   name='editor_hero_slide_save'),
    path('editor/api/site/hero/<int:slide_id>/delete/', editor_views.editor_hero_slide_delete, name='editor_hero_slide_delete'),

    # Stats & Achievement
    path('editor/api/site/stats/save/',       editor_views.editor_stats_save,       name='editor_stats_save'),
    path('editor/api/site/achievement/save/', editor_views.editor_achievement_save, name='editor_achievement_save'),

    # Ministry Section & Ministries
    path('editor/api/site/ministry-section/save/',            editor_views.editor_ministry_section_save, name='editor_ministry_section_save'),
    path('editor/api/site/ministries/add/',                   editor_views.editor_ministry_add,          name='editor_ministry_add'),
    path('editor/api/site/ministries/<int:ministry_id>/save/',   editor_views.editor_ministry_save,      name='editor_ministry_save'),
    path('editor/api/site/ministries/<int:ministry_id>/delete/', editor_views.editor_ministry_delete,    name='editor_ministry_delete'),

    # Gallery
    path('editor/api/site/gallery/add/',                    editor_views.editor_gallery_add,    name='editor_gallery_add'),
    path('editor/api/site/gallery/<int:gallery_id>/save/',   editor_views.editor_gallery_save,   name='editor_gallery_save'),
    path('editor/api/site/gallery/<int:gallery_id>/delete/', editor_views.editor_gallery_delete, name='editor_gallery_delete'),

    # About
    path('editor/api/site/about/save/',                      editor_views.editor_about_page_save,      name='editor_about_page_save'),
    path('editor/api/site/mission-vision/save/',             editor_views.editor_mission_vision_save,  name='editor_mission_vision_save'),
    path('editor/api/site/board-members/add/',               editor_views.editor_board_member_add,     name='editor_board_member_add'),
    path('editor/api/site/board-members/<int:member_id>/save/',   editor_views.editor_board_member_save,   name='editor_board_member_save'),
    path('editor/api/site/board-members/<int:member_id>/delete/', editor_views.editor_board_member_delete, name='editor_board_member_delete'),
    # About — Ministry pillars
    path('editor/api/site/about-ministries/add/',                    editor_views.editor_about_ministry_add,    name='editor_about_ministry_add'),
    path('editor/api/site/about-ministries/<int:ministry_id>/save/', editor_views.editor_about_ministry_save,   name='editor_about_ministry_save'),
    path('editor/api/site/about-ministries/<int:ministry_id>/delete/', editor_views.editor_about_ministry_delete, name='editor_about_ministry_delete'),
    # About — Challenges
    path('editor/api/site/challenge/save/', editor_views.editor_challenge_save, name='editor_challenge_save'),

    # Projects
    path('editor/api/site/projects-page/save/',              editor_views.editor_projects_page_save, name='editor_projects_page_save'),
    path('editor/api/site/projects/add/',                    editor_views.editor_project_add,        name='editor_project_add'),
    path('editor/api/site/projects/<int:project_id>/save/',   editor_views.editor_project_save,       name='editor_project_save'),
    path('editor/api/site/projects/<int:project_id>/delete/', editor_views.editor_project_delete,     name='editor_project_delete'),

    # Volunteer
    path('editor/api/site/volunteer/save/', editor_views.editor_site_volunteer_save, name='editor_site_volunteer_save'),

    # Give / Donate
    path('editor/api/site/give/save/',                         editor_views.editor_site_give_save,       name='editor_site_give_save'),
    path('editor/api/site/bank-accounts/add/',                 editor_views.editor_bank_account_add,     name='editor_bank_account_add'),
    path('editor/api/site/bank-accounts/<int:account_id>/save/',   editor_views.editor_bank_account_save,   name='editor_bank_account_save'),
    path('editor/api/site/bank-accounts/<int:account_id>/delete/', editor_views.editor_bank_account_delete, name='editor_bank_account_delete'),

    # Media
    path('editor/api/site/media/save/',                       editor_views.editor_site_media_save, name='editor_site_media_save'),
    path('editor/api/site/videos/add/',                       editor_views.editor_video_add,       name='editor_video_add'),
    path('editor/api/site/videos/<int:video_id>/save/',        editor_views.editor_video_save,      name='editor_video_save'),
    path('editor/api/site/videos/<int:video_id>/delete/',      editor_views.editor_video_delete,    name='editor_video_delete'),
    path('editor/api/site/podcasts/add/',                      editor_views.editor_podcast_add,     name='editor_podcast_add'),
    path('editor/api/site/podcasts/<int:podcast_id>/save/',    editor_views.editor_podcast_save,    name='editor_podcast_save'),
    path('editor/api/site/podcasts/<int:podcast_id>/delete/',  editor_views.editor_podcast_delete,  name='editor_podcast_delete'),

    # Blog Editor
    path('editor/blog/', editor_views.editor_blog_list, name='editor_blog_list'),
    path('editor/blog/new/', editor_views.editor_blog_new, name='editor_blog_new'),
    path('editor/blog/<int:post_id>/', editor_views.editor_blog_edit, name='editor_blog_edit'),
    path('editor/api/blog/save/', editor_views.editor_blog_save, name='editor_blog_save'),
    path('editor/api/blog/<int:post_id>/save/', editor_views.editor_blog_save, name='editor_blog_save_update'),
    path('editor/api/blog/<int:post_id>/delete/', editor_views.editor_blog_delete, name='editor_blog_delete'),

    # Serve media files in all environments (including production/DEBUG=False)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]