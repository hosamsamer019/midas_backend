from django.contrib import admin
from .models import Message, MessageAttachment

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'subject', 'timestamp', 'read_status', 'message_type', 'is_archived']
    list_filter = ['read_status', 'timestamp', 'sender', 'recipient', 'message_type', 'is_archived', 'department']
    search_fields = ['subject', 'content', 'sender__username', 'recipient__username']
    readonly_fields = ['timestamp']
    raw_id_fields = ['content_type']

@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ['message', 'file', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['message__subject', 'file']
    readonly_fields = ['uploaded_at']
