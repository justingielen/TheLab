import debug_toolbar
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),
    path('', views.welcome, name='welcome'),
    path('discover_drills/', views.discover_drills, name='discover_drills'),
    path('whatisthelab/', views.whatisthelab, name = 'whatis-thelab'),
    path('about/', views.about, name='about'),
    path('createprofile/', views.CustomSignupView.as_view(), name='createprofile'),
    path('auth/google/callback/', views.google_auth_callback, name='google_auth_callback'),
    path('accounts/', include('allauth.urls')),  # This includes all other allauth URLs    
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name = 'login'), # Django-provided view
    path('logout/', auth_views.LogoutView.as_view(template_name='main/logout.html'), name = 'logout'), # Django-provided view
    path('home/', views.home, name='home'),
    path('alerts/', views.alerts, name='alerts'),
    path('alerts/<int:notification_id>/read/', views.read_notification, name='read_notification'),
    path('profile_edit/', views.profile_edit, name='profile_edit'),
    path('application/', views.application, name='application'),
    path('page/', include('page.urls')),
    path('schedule/', include('schedule.urls')),
    path('events/', include('events.urls')),
]

# Slight modification from Django documentation about serving files uploaded by a user during !development! I use this to display 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)