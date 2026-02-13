from django.contrib import admin
from .models import ChatMessage, KnowledgeBase

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'response', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('message', 'response')
    readonly_fields = ('timestamp',)

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('content', 'source', 'id')
    list_filter = ('source',)
    search_fields = ('content', 'source')
    readonly_fields = ('id',)
