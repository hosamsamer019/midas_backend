from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    response = models.TextField()
    sources = models.JSONField(default=list, help_text="List of sources used for the response")
    source_type = models.CharField(max_length=50, choices=[
        ('kb', 'Knowledge Base'),
        ('llm', 'External LLM'),
        ('mixed', 'Mixed')
    ], default='kb')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_phi_detected = models.BooleanField(default=False)
    phi_anonymized = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Chat by {self.user.username} at {self.timestamp}"

class KnowledgeBase(models.Model):
    content = models.TextField(help_text="Chunk of text from knowledge base")
    source = models.CharField(max_length=255, help_text="Source file or document")
    embedding = models.JSONField(help_text="Vector embedding for similarity search")
    metadata = models.JSONField(default=dict, help_text="Additional metadata")

    def __str__(self):
        return f"KB Chunk from {self.source}: {self.content[:50]}..."
