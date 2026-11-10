from rest_framework import serializers


class EstadoSerializer(serializers.Serializer):
    exito = serializers.BooleanField()
    mensaje = serializers.CharField()
    servicio = serializers.CharField()
    version = serializers.CharField()
