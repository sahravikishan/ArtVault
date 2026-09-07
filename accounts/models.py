from django.db import models
from django.contrib.auth.models import User
from paintings.models import Painting


class CollectorProfile(models.Model):
    """Dedicated data store for regular Collectors / Buyers."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='collector_profile')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=25, blank=True)
    shipping_address = models.TextField(blank=True)
    # Direct relationship to Artist account if the same person registers as both
    linked_artist = models.OneToOneField(
        'artists.Artist',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_collector'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Collector Profile'
        verbose_name_plural = 'Collector Profiles'

    def __str__(self):
        return f'{self.name} ({self.email})'


class Favourite(models.Model):
    """A painting saved/hearted by a logged-in collector."""
    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourites')
    painting = models.ForeignKey(Painting, on_delete=models.CASCADE, related_name='favourited_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-saved_at']
        unique_together = ('user', 'painting')   # one heart per painting per user

    def __str__(self):
        return f'{self.user.username} → {self.painting.title}'
