from rest_framework import serializers


class SolicitudRegistroSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tipo = serializers.CharField()
    dni = serializers.CharField()
    nombreCompleto = serializers.CharField()
    telefono = serializers.CharField(allow_null=True)
    placaNumero = serializers.CharField(allow_null=True)
    rutaTrabajo = serializers.CharField(allow_null=True)
    estado = serializers.CharField()
    usuarioAsignado = serializers.CharField(allow_null=True)
    creadoEn = serializers.DateTimeField()
    actualizadoEn = serializers.DateTimeField(allow_null=True)


class CrearCambioRutaSerializer(serializers.Serializer):
    tipo = serializers.CharField()
    usuarioId = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    lineaSolicitadaId = serializers.IntegerField()


class ResolverSolicitudSerializer(serializers.Serializer):
    estado = serializers.CharField()
    usuarioAsignado = serializers.CharField(required=False, allow_blank=True, allow_null=True)
