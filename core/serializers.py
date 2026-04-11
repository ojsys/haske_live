from rest_framework import serializers
from core.models import DemographicData

class DemographicDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemographicData
        fields = '__all__'
