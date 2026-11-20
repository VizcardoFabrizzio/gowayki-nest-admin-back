from django.urls import include, path

from src.presentation.views.estado import EstadoView

urlpatterns = [
    path("estado", EstadoView.as_view(), name="estado"),
    path("", include("src.presentation.urls.auth")),
    path("", include("src.presentation.urls.usuario")),
    path("", include("src.presentation.urls.linea")),
    path("", include("src.presentation.urls.unidad")),
    path("", include("src.presentation.urls.solicitud_registro")),
]
