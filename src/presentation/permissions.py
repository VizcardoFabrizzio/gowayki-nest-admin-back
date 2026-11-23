from rest_framework.permissions import BasePermission


class EsAdmin(BasePermission):
    def has_permission(self, request, view):
        usuario = getattr(request, "user", None)
        return getattr(usuario, "rol", None) == "ADMIN"


class EsJefeRuta(BasePermission):
    def has_permission(self, request, view):
        usuario = getattr(request, "user", None)
        return getattr(usuario, "rol", None) == "JEFE_RUTA"


class EsAdminOJefeRuta(BasePermission):
    def has_permission(self, request, view):
        usuario = getattr(request, "user", None)
        return getattr(usuario, "rol", None) in {"ADMIN", "JEFE_RUTA"}
