from django.urls import path
from . import views

urlpatterns = [
    path('browsing/', views.page_browsing, name='page_browsing'),
    path('<pk>/viewing/', views.page_viewing, name='page_viewing'),
    path('<pk>/viewing/maps/', views.maps_links, name='maps_links'),
    path('search/location', views.search_location, name='location_search'),
    path('create/location/', views.create_location, name='location_form'),
    path('add/location/<str:name>/', views.add_location, name='add_location'),
    path('remove/location/<str:name>/', views.remove_location, name='remove_location'),
    path('set/availability/', views.set_availability, name='set_availability'),
    path('remove/availability/<str:availability_id>/', views.remove_availability, name='remove_availability'),
    path('create/package/', views.create_package, name='package_form'),
    path('create/package/custom_type/', views.custom_type, name='custom_package_type'),
    path('<pk>/select_location', views.select_location, name='select_location'),
    path('<pk>/<week>/check_availability', views.check_availability, name='check_availability'),
    path('<date>/<time>/<week>/signup/', views.signup, name='signup'),
    path('<pk>/viewing/accept_event/', views.accept_event, name='accept_event'),
    path('create/event/', views.create_event, name='event_form'),
    path('create/event/custom_type/', views.custom_type, name='custom_event_type'),
]