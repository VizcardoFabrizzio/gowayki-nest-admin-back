from django.urls import path

from src.presentation.views.usuario import UsuarioDetailView, UsuarioListView

urlpatterns = [
    path("usuarios", UsuarioListView.as_view(), name="usuario-list"),
    path("usuarios/<uuid:usuario_id>", UsuarioDetailView.as_view(), name="usuario-detail"),
]
