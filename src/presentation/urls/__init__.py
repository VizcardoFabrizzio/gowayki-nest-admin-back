from django.urls import path

from src.presentation.views.estado import EstadoView

urlpatterns = [
    path("estado", EstadoView.as_view(), name="estado"),
]
