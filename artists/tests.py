from django.test import TestCase, Client
from django.urls import reverse
from .models import Artist
from paintings.models import Painting


class ArtistViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.artist = Artist.objects.create(
            name='Helena Rostova',
            birth_year=1968,
            bio='Renowned contemporary painter specializing in large-scale oils.'
        )
        self.painting = Painting.objects.create(
            title='Twilight Over Saint Petersburg',
            artist=self.artist,
            year_created=2021,
            style='Impressionism',
            estimated_value=125000.00
        )

    def test_artist_directory_view(self):
        response = self.client.get(reverse('artists:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Helena Rostova')
        self.assertContains(response, '1 work archived')

    def test_artist_detail_view(self):
        response = self.client.get(reverse('artists:detail', args=[self.artist.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Helena Rostova')
        self.assertContains(response, 'Twilight Over Saint Petersburg')
        self.assertContains(response, '1,25,000')
