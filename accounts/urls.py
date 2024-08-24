from django.urls import path

from .views import (
    UserChangePasswordView,
    UserLoginView,
    UserLogoutView,
    UserProfileUpdateView,
    UserRegistrationView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("update_profile/", UserProfileUpdateView.as_view(), name="update_profile"),
    path("passwordChange/", UserChangePasswordView.as_view(), name="passwordChange"),
]
