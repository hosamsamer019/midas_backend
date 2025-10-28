from django.db import models
from users.models import User

class Upload(models.Model):
    file = models.FileField(upload_to='uploads/')
    file_type = models.CharField(max_length=50, choices=[
        ('excel', 'Excel File'),
        ('image', 'Image'),
        ('pdf', 'PDF'),
    ])
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.file_type} uploaded by {self.uploaded_by} on {self.uploaded_at}"
