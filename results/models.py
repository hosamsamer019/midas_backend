from django.db import models
from samples.models import Sample
from antibiotics.models import Antibiotic

class TestResult(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    antibiotic = models.ForeignKey(Antibiotic, on_delete=models.CASCADE)
    sensitivity = models.CharField(max_length=20, choices=[
        ('sensitive', 'Sensitive'),
        ('intermediate', 'Intermediate'),
        ('resistant', 'Resistant'),
    ])
    mic_value = models.FloatField(null=True, blank=True)
    zone_diameter = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('sample', 'antibiotic')

    def __str__(self):
        return f"{self.sample} - {self.antibiotic}: {self.sensitivity}"
