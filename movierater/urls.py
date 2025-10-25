"""movierater URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.conf.urls.static import static
from django.conf.urls import include
from rest_framework.authtoken.views import obtain_auth_token
from django.urls import re_path
from movierater import settings
from django.views.generic.base import RedirectView

favicon_view = RedirectView.as_view(url='favicon/favicon.ico', permanent=True)

urlpatterns = [
    path('favicon.ico/', favicon_view, name="favicon"),
    path('', include('home.urls')),
    # add a custom admin login page
    path('login/', LoginView.as_view(),
        {'template_name': 'core/login.html'}, name='login'),
    # include logout page as home for admin on logout
    path('admin/logout/', include('home.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('auth/', obtain_auth_token),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.conf.urls.static import static

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
