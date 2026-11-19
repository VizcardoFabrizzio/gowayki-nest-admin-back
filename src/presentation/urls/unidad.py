from django.urls import path

from src.presentation.views.unidad import (
    UnidadDetailView,
    UnidadListView,
    UnidadPorLineaListView,
)

urlpatterns = [
    path("unidades", UnidadListView.as_view(), name="unidad-list"),
    path("unidades/<int:unidad_id>", UnidadDetailView.as_view(), name="unidad-detail"),
    path(
        "lineas/<int:linea_id>/unidades",
        UnidadPorLineaListView.as_view(),
        name="linea-unidades",
    ),
]
