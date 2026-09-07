from django.db import models
from django.contrib.auth.models import User


class Artist(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='artist_profile'
    )
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='artists/', blank=True, null=True)
    birth_year = models.IntegerField(blank=True, null=True)
    payout_upi_id = models.CharField(max_length=100, blank=True, help_text='UPI ID for gallery sale payouts')
    payout_bank_details = models.TextField(blank=True, help_text='Bank account details for NEFT/RTGS transfers')
    is_verified_artist = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
