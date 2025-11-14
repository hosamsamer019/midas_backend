from django.db import models
from samples.models import Sample
from antibiotics.models import Antibiotic

class TestResult(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    antibiotic = models.ForeignKey(Antibiotic, on_delete=models.CASCADE)
    sensitivity = models.CharField(max_length=30, choices=[
        ('sensitive', 'Sensitive'),
        ('intermediate', 'Intermediate'),
        ('resistant', 'Resistant'),
        ('susceptible', 'Susceptible'),
        ('susceptible_dose_dependent', 'Susceptible Dose Dependent'),
        ('not_done', 'Not Done'),
        ('unknown', 'Unknown'),
    ])
    mic_value = models.CharField(max_length=50, null=True, blank=True)  # Changed to CharField for MIC ranges like ">=32"
    zone_diameter = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('sample', 'antibiotic')

    def __str__(self):
        return f"{self.sample} - {self.antibiotic}: {self.sensitivity}"
