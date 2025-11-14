
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('results', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testresult',
            name='mic_value',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='sensitivity',
            field=models.CharField(
                choices=[
                    ('sensitive', 'Sensitive'),
                    ('intermediate', 'Intermediate'),
                    ('resistant', 'Resistant'),
                    ('susceptible', 'Susceptible'),
                    ('susceptible_dose_dependent', 'Susceptible Dose Dependent'),
                    ('not_done', 'Not Done'),
                    ('unknown', 'Unknown'),
                ],
                max_length=30
            ),
        ),
    ]
