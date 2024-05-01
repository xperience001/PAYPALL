from django.urls import path
from django.contrib.auth import views as dj_auth_views
from .views import (
    CustomLoginView,
    RegisterView,
    DashBoardView,
    AccountsPageView,
)

app_name = "register"

urlpatterns = [
    path("", DashBoardView.as_view(), name="dashboard"),
    path("account", AccountsPageView.as_view(), name="account"),
    path("login", CustomLoginView.as_view(), name="login"),
    path("register", RegisterView.as_view(), name="register"),
    path("logout/", dj_auth_views.LogoutView.as_view(), name="logout"),
]
