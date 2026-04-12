from django.urls import path, include
from django.conf import settings
from .views import StateDemographicView, DemographicsMapView
from django.conf.urls.static import static
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
    
    path('ckeditor/', include('ckeditor_uploader.urls')),

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

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)