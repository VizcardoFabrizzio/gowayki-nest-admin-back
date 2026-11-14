from django.urls import path

from src.presentation.views.auth import LoginView, RegistroView

urlpatterns = [
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/registro", RegistroView.as_view(), name="auth-registro"),
]
