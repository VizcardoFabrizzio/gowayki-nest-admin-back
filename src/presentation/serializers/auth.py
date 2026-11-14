from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    dni = serializers.CharField(required=False, allow_blank=True, default="")
    pin = serializers.CharField(required=False, allow_blank=True, default="", trim_whitespace=False)


class RegistroSerializer(serializers.Serializer):
    nombre = serializers.CharField(required=False, allow_blank=True, default="")
    dni = serializers.CharField(required=False, allow_blank=True, default="")
    telefono = serializers.CharField(required=False, allow_blank=True, default="")
    email = serializers.CharField(required=False, allow_blank=True, allow_null=True, default=None)
    pin = serializers.CharField(required=False, allow_blank=True, default="", trim_whitespace=False)


class UsuarioSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    nombre = serializers.CharField()
    dni = serializers.CharField()
    telefono = serializers.CharField()
    email = serializers.CharField(allow_null=True)
    fotoUrl = serializers.CharField(allow_null=True)
    rol = serializers.CharField()
    isOnline = serializers.BooleanField()


class AuthResponseSerializer(serializers.Serializer):
    exito = serializers.BooleanField()
    mensaje = serializers.CharField()
    usuario = UsuarioSerializer()
