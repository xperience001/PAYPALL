from django.urls import path
from django.contrib.auth import views as dj_auth_views
from .views import CustomLoginView, RegisterView, DashBoardView

app_name = "register"

urlpatterns = [
    path("", DashBoardView.as_view(), name="dashboard"),
    path("auth/login/", CustomLoginView.as_view(), name="login"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/logout/", dj_auth_views.LogoutView.as_view(), name="logout"),
]
