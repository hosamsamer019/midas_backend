from django.db import models
from users.models import User
from bacteria.models import Bacteria

class Sample(models.Model):
    patient_id = models.CharField(max_length=50)
    bacteria = models.ForeignKey(Bacteria, on_delete=models.CASCADE)
    hospital = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Sample {self.id} - {self.patient_id}"
