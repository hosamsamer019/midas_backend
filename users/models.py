from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('lab_technician', 'Lab Technician'),
        ('doctor', 'Doctor'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='lab_technician')

    def __str__(self):
        return self.username
