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
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .api import views

from myapp.spa.views import SpaView
from myapp.api.views import GreetingApi

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/greet", GreetingApi.as_view()),
    
    # Loads registration/login.html
    path("", SpaView.as_view(), name="spa"),

    # Include all Django Authentication pages
    path("accounts/register/", views.sign_up, name="register"),
    path("accounts/login/", views.log_in, name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/password_reset/", auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"), name="password-reset"),
    path("accounts/", include("django.contrib.auth.urls")),
]

    #path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login")