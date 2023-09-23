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
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from .api import views

from myapp.spa.views import SpaView
from myapp.api.views import GreetingApi

# turn off formatting by 'black'
# fmt: off
urlpatterns = [
<<<<<<< HEAD
    path("admin/", admin.site.urls),
    path("api/greet", GreetingApi.as_view()),
     # Django Authentication pages
    path("accounts/register/", views.register, name="register"),
    path("accounts/register_success/<str:email>/", views.register_success, name="register_success"),
    path("accounts/login/", views.log_in, name="login"),
    path("accounts/logout/", views.log_out, name="logout"),
    path("accounts/password_reset/", views.password_reset, name="password_reset"),
    path("accounts/password_reset/done/", views.password_reset_done, name="password_reset_done"),
    path("accounts/password_reset/confirm/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
    path("accounts/password_reset/complete/<str:email>/", views.password_reset_complete, name="password_reset_complete"),
    #Catch All URL
    re_path(r'^.*$', SpaView.as_view(), name="spa"),
]
=======
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "api/greet",
        GreetingApi.as_view(),
    ),
    # Loads registration/login.html
    path(
        "accounts/register/",
        views.register,
        name="register",
    ),
    path(
        "accounts/login/",
        views.log_in,
        name="login",
    ),
    path(
        "accounts/logout/",
        views.log_out,
        name="logout",
    ),
    path(
        "accounts/password_reset/",
        views.password_reset,
        name="password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        views.password_reset_done,
        name="password_reset_done",
    ),
    path(
        "accounts/password_reset/confirm/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path(
        "accounts/password_reset/complete/<str:email>/",
        views.password_reset_complete,
        name="password_reset_complete",
    ),
    path(
        "inductee_form/",
        views.inductee_form,
        name="inductee_form",
    ),
    path(
        "inductee_form_complete/",
        views.inductee_form_complete,
        name="inductee_form_complete",
    ),
    path(
        "outreach_form/",
        views.outreach_form,
        name="outreach_form",
    ),
    path(
        "outreach_form_complete/",
        views.outreach_form_complete,
        name="outreach_form_complete",
    ),
    # Catch all URL
    re_path(
        r'^.*$',
        SpaView.as_view(),
        name="spa"
    ),
]
>>>>>>> temp_branch
