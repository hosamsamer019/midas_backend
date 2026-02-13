from rest_framework import serializers
from django.contrib.auth import get_user_model
from bacteria.models import Bacteria
from antibiotics.models import Antibiotic
from samples.models import Sample
from results.models import TestResult
from uploads.models import Upload
from ai_recommendations.models import AIRecommendation

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role_id.role_name', read_only=True)
    id = serializers.IntegerField(source='user_id', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'user_id', 'full_name', 'email', 'role_id', 'role_name', 'status', 'create_at', 'last_login']
        read_only_fields = ['user_id', 'create_at', 'last_login']

class RegisterSerializer(serializers.ModelSerializer):
    """Admin-only user registration serializer"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)
    full_name = serializers.CharField(required=True)
    role_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'role_id']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_role_id(self, value):
        from users.models import Role
        try:
            Role.objects.get(pk=value)
        except Role.DoesNotExist:
            raise serializers.ValidationError(f"Role with id {value} does not exist.")
        return value

    def create(self, validated_data):
        from users.models import Role
        role_id = validated_data.pop('role_id')
        role = Role.objects.get(pk=role_id)
        user = User.objects.create_user(role=role, **validated_data)
        return user

class BacteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bacteria
        fields = '__all__'

class AntibioticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Antibiotic
        fields = '__all__'

class SampleSerializer(serializers.ModelSerializer):
    bacteria_name = serializers.CharField(source='bacteria.name', read_only=True)

    class Meta:
        model = Sample
        fields = '__all__'

class TestResultSerializer(serializers.ModelSerializer):
    sample_details = SampleSerializer(source='sample', read_only=True)
    antibiotic_name = serializers.CharField(source='antibiotic.name', read_only=True)

    class Meta:
        model = TestResult
        fields = '__all__'

class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload
        fields = '__all__'

class AIRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIRecommendation
        fields = '__all__'
