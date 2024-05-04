"""
URL configuration for thelab project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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
    path('home/', views.home, name='home'),
    path('alerts/', views.alerts, name='alerts'),
    path('discover_drills/', views.discover_drills, name='discover_drills'),
    path('whatisthelab/', views.whatisthelab, name = 'whatis-thelab'),
    path('about/', views.about, name='about'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name = 'login'), # Django-provided view
    path('logout/', auth_views.LogoutView.as_view(template_name='main/logout.html'), name = 'logout'), # Django-provided view
    path('createprofile/', views.createprofile, name = 'createprofile'),
    path('profile_edit/', views.profile_edit, name='profile_edit'), # Could convert to class based view and incorporate Team Approvals (some front-end functionality is written but unused)
    path('team_application/', views.team_application, name='team_application'),
    path('page/', include('page.urls')),
    path('schedule/', include('schedule.urls')),
    path('events/', include('events.urls')),
]

# Slight modification from Django documentation about serving files uploaded by a user during !development! I use this to display 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)