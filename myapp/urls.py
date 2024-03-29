"""
URL configuration for myapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from myapp.api.views import user_views

from myapp.spa.views import SpaView

# turn off formatting by 'black'
# fmt: off
urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "api/",
        include("myapp.api.urls"),
    ),
    # Loads registration/login.html
    path(
        "accounts/register/",
        user_views.register,
        name="register",
    ),
    path(
        "accounts/login/",
        user_views.log_in,
        name="login",
    ),
    path(
        "accounts/logout/",
        user_views.log_out,
        name="logout",
    ),
    path(
        "accounts/password_reset/",
        user_views.password_reset,
        name="password_reset",
    ),
    path(
        "accounts/password_reset_done/",
        user_views.password_reset_done,
        name="password_reset_done",
    ),
    path(
        "accounts/password_reset/confirm/<uidb64>/<token>/",
        user_views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path(
        "accounts/password_reset/complete/<str:email>/",
        user_views.password_reset_complete,
        name="password_reset_complete",
    ),
    path(
        "inductee_form/<token>/",
        user_views.inductee_form,
        name="inductee_form",
    ),
    path(
        "inductee_form_complete/",
        user_views.inductee_form_complete,
        name="inductee_form_complete",
    ),
    path(
        "outreach_form/<token>/",
        user_views.outreach_form,
        name="outreach_form",
    ),
    path(
        "outreach_form_complete/",
        user_views.outreach_form_complete,
        name="outreach_form_complete",
    ),
    path(
        "email/event/<int:event_pk>/",
        user_views.email_view,
        name="email_events"
    ),
    # Catch all URL
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    re_path(
        r'^.*$',
        SpaView.as_view(),
        name="spa"
    ),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
