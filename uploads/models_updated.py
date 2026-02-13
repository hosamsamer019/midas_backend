from django.db import models
from users.models import User

class Upload(models.Model):
    APPROVAL_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    file = models.FileField(upload_to='uploads/')
    file_type = models.CharField(max_length=50, choices=[
        ('excel', 'Excel File'),
        ('image', 'Image'),
        ('pdf', 'PDF'),
    ])
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_uploads')
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.file_type} uploaded by {self.uploaded_by} on {self.uploaded_at} - {self.approval_status}"
