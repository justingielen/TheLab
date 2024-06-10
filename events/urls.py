from django.urls import path
from . import views # from the current folder

# URL Configuration
urlpatterns = [
    path('browsing/', views.EventListView.as_view(), name='browse_events'), # Class Based ListView
    path('<pk>/viewing/', views.EventDetailView.as_view(), name='view_event'), # Class based DetailView -- <pk> is the private key of whatever Event you're viewing (First url with a variable-- will be used in page viewing)
    path('<pk>/signup/', views.create_attendee, name='attendee_form')
]
