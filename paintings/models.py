from django.db import models
from artists.models import Artist


class Painting(models.Model):
    STYLE_CHOICES = [
        ('Realism', 'Realism'),
        ('Impressionism', 'Impressionism'),
        ('Abstract', 'Abstract'),
        ('Surrealism', 'Surrealism'),
        ('Other', 'Other'),
    ]

    title = models.CharField(max_length=300)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    year_created = models.IntegerField()
    style = models.CharField(max_length=50, choices=STYLE_CHOICES, default='Other')
    story = models.TextField(blank=True)
    materials = models.CharField(max_length=300, blank=True)
    dimensions = models.CharField(max_length=200, blank=True)
    current_location = models.CharField(max_length=300, blank=True, null=True)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='paintings/', blank=True, null=True)

    class Meta:
        ordering = ['-year_created']

    def __str__(self):
        return f'{self.title} ({self.year_created})'
