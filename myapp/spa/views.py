from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.shortcuts import redirect


class SpaView(LoginRequiredMixin, TemplateView):
    template_name = "spa/index.html"


def logout_view(request):
    logout(request)
    return redirect("/accounts/login")
