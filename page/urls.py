from django.urls import path
from . import views

urlpatterns = [
    path('browsing/', views.page_browsing, name='page_browsing'),
    path('<pk>/viewing/', views.page_viewing, name='page_viewing'),
    path('create/event/', views.create_event, name='event_form'),
    path('create/location/', views.create_location, name='location_form'),
    path('search/location', views.search_location, name='location_search'),
    path('add/location/<str:location_name>/', views.add_location, name='add_location'),
    path('remove/location/<str:location_name>/', views.remove_location, name='remove_location'),
    path('create/package/', views.create_package, name='package_form'),
]