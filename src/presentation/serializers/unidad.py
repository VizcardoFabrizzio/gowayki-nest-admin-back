from rest_framework import serializers


class PosicionGpsSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    velocidadKmh = serializers.FloatField()
    rumboGrados = serializers.IntegerField()
    ultimaActualizacion = serializers.DateTimeField()


class UnidadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    numeroPadron = serializers.CharField()
    placa = serializers.CharField()
    lineaId = serializers.IntegerField()
    lineaNombre = serializers.CharField(allow_null=True)
    estado = serializers.CharField()
    posicionActual = PosicionGpsSerializer(allow_null=True)


class CrearUnidadSerializer(serializers.Serializer):
    numeroPadron = serializers.CharField(
        max_length=10, required=False, allow_blank=True, default=""
    )
    placa = serializers.CharField(max_length=10)
    lineaId = serializers.IntegerField()
    estado = serializers.CharField(
        max_length=20, required=False, allow_blank=False, default="OPERATIVA"
    )


class ActualizarUnidadSerializer(serializers.Serializer):
    numeroPadron = serializers.CharField(max_length=10, required=False, allow_blank=True)
    placa = serializers.CharField(max_length=10, required=False, allow_blank=False)
    lineaId = serializers.IntegerField(required=False)
    estado = serializers.CharField(max_length=20, required=False, allow_blank=False)
