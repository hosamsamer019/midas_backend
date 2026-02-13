from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Message(models.Model):
    MESSAGE_TYPES = [
        ('direct', 'Direct Message'),
        ('contextual', 'Contextual Message'),
        ('broadcast', 'Broadcast Message'),
    ]

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_messages')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='direct')
    is_archived = models.BooleanField(default=False)

    # Contextual linking
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Additional context fields
    department = models.CharField(max_length=100, null=True, blank=True)
    date_range_start = models.DateField(null=True, blank=True)
    date_range_end = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        sender_name = getattr(self.sender, 'username', '<deleted user>') if self.sender else '<deleted user>'
        if self.message_type == 'broadcast':
            return f"Broadcast from {sender_name}: {self.subject}"
        elif self.recipient:
            recipient_name = getattr(self.recipient, 'username', '<deleted user>') if self.recipient else '<deleted user>'
            return f"From {sender_name} to {recipient_name}: {self.subject}"
        else:
            return f"From {sender_name}: {self.subject}"

class MessageAttachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='message_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.message}: {self.file.name}"
