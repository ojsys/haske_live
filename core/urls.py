from django.urls import path, include
from django.conf import settings
from .views import StateDemographicView, DemographicsMapView
from django.conf.urls.static import static
from . import views

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

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)