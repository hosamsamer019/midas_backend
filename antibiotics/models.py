from django.db import models

class Antibiotic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100)
    mechanism = models.CharField(max_length=200)
    common_use = models.CharField(max_length=200)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name
