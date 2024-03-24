from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from .forms import SignUpForm
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


class CustomLoginView(LoginView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your custom context here
        context["title"] = "Account Login"
        return context


class RegisterView(CreateView):
    form_class = SignUpForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("register:dashboard")

    def form_valid(self, form):
        user = form.save()

        if user:
            login(self.request, user)

        return super().form_valid(form)


class DashBoardView(LoginRequiredMixin, TemplateView):
    template_name = "user/dashboard.html"
