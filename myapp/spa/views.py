from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect
<<<<<<< HEAD
=======

>>>>>>> temp_branch

class SpaView(LoginRequiredMixin, TemplateView):
    template_name = "spa/index.html"

    def get(self, request, *args, **kwargs):
<<<<<<< HEAD
        return render(request, 'spa/index.html')
=======
        return render(request, "spa/index.html")
>>>>>>> temp_branch
