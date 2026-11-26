from django.urls import path

from src.presentation.views.usuario import (
    UsuarioDetailView,
    UsuarioListView,
    UsuarioSubrutaView,
)

urlpatterns = [
    path("usuarios", UsuarioListView.as_view(), name="usuario-list"),
    path("usuarios/<uuid:usuario_id>", UsuarioDetailView.as_view(), name="usuario-detail"),
    path(
        "usuarios/<uuid:usuario_id>/subruta", UsuarioSubrutaView.as_view(), name="usuario-subruta"
    ),
]
