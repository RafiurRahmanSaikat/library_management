from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView

from library.views import send_transaction_email

from .forms import UserLoginForm, UserRegistrationForm, UserUpdateForm

# Create your views here.


class UserRegistrationView(FormView):
    template_name = "accounts/user_registration.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "register"
        return context

    def form_valid(self, form):
        try:
            user = form.save()
            login(self.request, user)
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(
                "This username is already exisr.",
            )
            return self.form_invalid(form)


class UserLoginView(LoginView):
    template_name = "accounts/user_registration.html"
    form_class = UserLoginForm  # Specify the form class

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "login"
        return context

    def get_success_url(self):
        return reverse_lazy("home")


class UserLogoutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy("home")


class UserProfileUpdateView(View):
    template_name = "accounts/user_registration.html"

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {"form": form, "title": "update"})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
        return render(request, self.template_name, {"form": form, "title": "update"})


class UserChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/change_password.html"
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        send_transaction_email(
            self.request.user,
            "",
            "Your Password Has Been Changed",
            "accounts/password_change_email.html",
        )

        return super().form_valid(form)
