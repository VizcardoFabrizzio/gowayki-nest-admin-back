from django.urls import path

from src.presentation.views.linea import LineaDetailView, LineaListView
from src.presentation.views.punto_control import PuntoControlListView

urlpatterns = [
    path("lineas", LineaListView.as_view(), name="linea-list"),
    path("lineas/<int:linea_id>", LineaDetailView.as_view(), name="linea-detail"),
    path(
        "lineas/<int:linea_id>/puntos-control",
        PuntoControlListView.as_view(),
        name="linea-puntos-control",
    ),
]
