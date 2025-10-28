from django.db import models

class Bacteria(models.Model):
    name = models.CharField(max_length=100, unique=True)
    bacteria_type = models.CharField(max_length=50, choices=[
        ('gram_positive', 'Gram Positive'),
        ('gram_negative', 'Gram Negative'),
    ])
    gram_stain = models.CharField(max_length=50)
    source = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name
