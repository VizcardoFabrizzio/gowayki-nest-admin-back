from django.urls import path

from src.presentation.views.solicitud_registro import (
    SolicitudRegistroDetailView,
    SolicitudRegistroListView,
)

urlpatterns = [
    path(
        "solicitudes-registro",
        SolicitudRegistroListView.as_view(),
        name="solicitud-registro-list",
    ),
    path(
        "solicitudes-registro/<int:solicitud_id>",
        SolicitudRegistroDetailView.as_view(),
        name="solicitud-registro-detail",
    ),
]
