from rest_framework import serializers


class PuntoControlSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    orden = serializers.IntegerField()
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    radioMetros = serializers.IntegerField()
    toleranciaMinutos = serializers.IntegerField()
