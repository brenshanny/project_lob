from rest_framework import serializers
from graphsite.models import Tank, Reading

class TankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tank
        fields = ('id', 'tank_id', 'name')

class ReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reading
        fields = ('id', 'reading_type', 'timestamp', 'value', 'tank')
