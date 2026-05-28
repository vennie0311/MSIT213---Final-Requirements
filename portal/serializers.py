from rest_framework import serializers

from .models import ScholarshipApplication


class ScholarshipApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarshipApplication
        fields = ['id', 'title', 'region', 'status', 'submitted_at']
