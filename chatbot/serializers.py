from rest_framework import serializers
from .models import ChatMessage, KnowledgeBase

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'message', 'response', 'sources', 'source_type', 'timestamp', 'is_phi_detected']
        read_only_fields = ['id', 'response', 'sources', 'source_type', 'timestamp', 'is_phi_detected']

class KnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = '__all__'
