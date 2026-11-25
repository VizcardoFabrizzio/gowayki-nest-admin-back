from rest_framework import serializers


class ActualizarRolSerializer(serializers.Serializer):
    rol = serializers.CharField(required=False, allow_blank=True, default="")


class ActualizarSubrutaSerializer(serializers.Serializer):
    subrutaId = serializers.IntegerField(required=True)


class UsuarioSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    nombre = serializers.CharField()
    dni = serializers.CharField()
    telefono = serializers.CharField()
    email = serializers.CharField(allow_null=True)
    fotoUrl = serializers.CharField(allow_null=True)
    rol = serializers.CharField()
    isOnline = serializers.BooleanField()
    lineaId = serializers.IntegerField(allow_null=True)
    lineaNombre = serializers.CharField(allow_null=True)
    subrutaId = serializers.IntegerField(allow_null=True)
    subrutaNombre = serializers.CharField(allow_null=True)
