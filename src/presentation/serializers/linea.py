from rest_framework import serializers


class LineaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    origen = serializers.CharField()
    destino = serializers.CharField()
    corredor = serializers.CharField(allow_null=True)
    colorHex = serializers.CharField()


class CrearLineaSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=50)
    origen = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    destino = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    corredor = serializers.CharField(
        max_length=50, required=False, allow_blank=True, allow_null=True
    )
    colorHex = serializers.CharField(max_length=7, required=False, allow_blank=False)


class ActualizarLineaSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=50, required=False, allow_blank=False)
    origen = serializers.CharField(max_length=100, required=False, allow_blank=True)
    destino = serializers.CharField(max_length=100, required=False, allow_blank=True)
    corredor = serializers.CharField(
        max_length=50, required=False, allow_blank=True, allow_null=True
    )
    colorHex = serializers.CharField(max_length=7, required=False, allow_blank=False)
