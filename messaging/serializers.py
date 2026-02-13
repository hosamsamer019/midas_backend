from rest_framework import serializers
from .models import Message, MessageAttachment

class MessageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageAttachment
        fields = ['id', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    attachments = MessageAttachmentSerializer(many=True, read_only=True)
    content_object_type = serializers.SerializerMethodField()
    content_object_repr = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_username', 'recipient', 'recipient_username',
                 'subject', 'content', 'timestamp', 'read_status', 'message_type',
                 'is_archived', 'content_type', 'object_id', 'content_object_type',
                 'content_object_repr', 'department', 'date_range_start', 'date_range_end',
                 'attachments']
        read_only_fields = ['id', 'timestamp', 'sender_username', 'recipient_username',
                           'content_object_type', 'content_object_repr']

    def get_content_object_type(self, obj):
        if obj.content_object:
            return obj.content_object.__class__.__name__
        return None

    def get_content_object_repr(self, obj):
        if obj.content_object:
            return str(obj.content_object)
        return None

class MessageCreateSerializer(serializers.ModelSerializer):
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True
    )
    recipient = serializers.PrimaryKeyRelatedField(
        queryset=Message._meta.get_field('recipient').remote_field.model.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'content', 'message_type', 'content_type',
                 'object_id', 'department', 'date_range_start', 'date_range_end', 'attachments']

    def create(self, validated_data):
        attachments = validated_data.pop('attachments', [])
        validated_data['sender'] = self.context['request'].user
        message = super().create(validated_data)

        # Create attachments
        for attachment in attachments:
            MessageAttachment.objects.create(message=message, file=attachment)

        return message
