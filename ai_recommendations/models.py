from django.db import models
from samples.models import Sample
from antibiotics.models import Antibiotic

class AIRecommendation(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    recommended_antibiotic = models.ForeignKey(Antibiotic, on_delete=models.CASCADE)
    confidence_score = models.FloatField()
    reasoning = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Recommendation for {self.sample}: {self.recommended_antibiotic}"
