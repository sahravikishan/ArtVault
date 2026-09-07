from django.test import TestCase, Client
from django.urls import reverse
from artists.models import Artist
from paintings.models import Painting, Order, Exhibition, Inquiry


class PaintingPlatformTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.artist = Artist.objects.create(name='Anya Sharma', birth_year=1980)
        self.painting1 = Painting.objects.create(
            title='Resonance of Indigo',
            artist=self.artist,
            year_created=2024,
            style='Abstract',
            materials='Oil on hand-woven linen',
            dimensions='120 x 90 cm',
            estimated_value=95000.00
        )
        self.painting2 = Painting.objects.create(
            title='Courtyard in Jaipur',
            artist=self.artist,
            year_created=2020,
            style='Realism',
            materials='Tempera on panel',
            dimensions='60 x 45 cm',
            estimated_value=45000.00
        )
        self.exhibition = Exhibition.objects.create(
            title='Visions of Pigment',
            slug='visions-of-pigment',
            subtitle='Chromatic Exploration',
            curator_statement='An essay exploring the material presence of mineral pigments in South Asian modernism.',
            curator_name='Dr. Elena Vance',
            is_ongoing=True
        )
        self.exhibition.paintings.add(self.painting1)

    def test_home_and_search(self):
        # Home
        res = self.client.get(reverse('paintings:home'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Resonance of Indigo')
        self.assertContains(res, 'Courtyard in Jaipur')

        # Style filter
        res_filter = self.client.get(reverse('paintings:home') + '?style=Abstract')
        self.assertContains(res_filter, 'Resonance of Indigo')
        self.assertNotContains(res_filter, 'Courtyard in Jaipur')

        # Search query
        res_search = self.client.get(reverse('paintings:home') + '?q=Jaipur')
        self.assertContains(res_search, 'Courtyard in Jaipur')
        self.assertNotContains(res_search, 'Resonance of Indigo')

    def test_painting_detail(self):
        res = self.client.get(reverse('paintings:detail', args=[self.painting1.pk]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Resonance of Indigo')
        self.assertContains(res, 'Visions of Pigment')  # exhibition callout

    def test_certificate_of_authenticity(self):
        order = Order.objects.create(
            painting=self.painting1,
            buyer_name='Karan Kapoor',
            buyer_email='karan@domain.com',
            buyer_phone='+91 99999 11111',
            amount=self.painting1.estimated_value,
            razorpay_order_id='rzp_order_coa_test',
            razorpay_payment_id='rzp_pay_coa_test',
            status='paid'
        )
        res = self.client.get(reverse('paintings:certificate', args=[order.pk]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Certificate of Authenticity')
        self.assertContains(res, 'Karan Kapoor')
        self.assertContains(res, order.certificate_number)

    def test_exhibition_views(self):
        # List
        res_list = self.client.get(reverse('paintings:exhibition_list'))
        self.assertEqual(res_list.status_code, 200)
        self.assertContains(res_list, 'Visions of Pigment')

        # Detail
        res_det = self.client.get(reverse('paintings:exhibition_detail', args=[self.exhibition.slug]))
        self.assertEqual(res_det.status_code, 200)
        self.assertContains(res_det, 'Visions of Pigment')
        self.assertContains(res_det, 'Resonance of Indigo')

    def test_curatorial_inquiry_submission(self):
        res = self.client.post(
            reverse('paintings:inquire', args=[self.painting1.pk]),
            {
                'name': 'Radhika Birla',
                'email': 'radhika@birla-art.org',
                'phone': '+91 98200 12345',
                'inquiry_type': 'condition_report',
                'message': 'Requesting conservation documentation for museum loan.'
            },
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['status'], 'success')
        self.assertTrue(Inquiry.objects.filter(collector_email='radhika@birla-art.org').exists())
