from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from artists.models import Artist
from paintings.models import Painting, Order
from accounts.models import CollectorProfile, Favourite


class AccountsAndArtistPortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.artist_user = User.objects.create_user(
            username='artist@artvault.in',
            email='artist@artvault.in',
            password='ArtistPassword123!',
            first_name='Devraj',
            last_name='Patel',
        )
        self.artist = Artist.objects.create(
            user=self.artist_user,
            name='Devraj Patel',
            birth_year=1975,
            bio='Master of Indian contemporary landscapes.',
            payout_upi_id='devraj@upi',
            payout_bank_details='HDFC Bank, A/C 9876543210, IFSC HDFC0001234'
        )
        self.painting = Painting.objects.create(
            title='Varanasi Ghats at Dawn',
            artist=self.artist,
            year_created=2023,
            style='Realism',
            estimated_value=Decimal('100000.00'),
            materials='Oil on Belgian linen',
            dimensions='100 x 120 cm'
        )
        self.collector = User.objects.create_user(
            username='collector@vault.in',
            email='collector@vault.in',
            password='CollectorPassword123!',
            first_name='Ananya',
            last_name='Sharma',
        )
        self.collector_profile = CollectorProfile.objects.create(
            user=self.collector,
            name='Ananya Sharma',
            email='collector@vault.in',
        )

    def test_collector_registration(self):
        """Registering as a collector redirects to My Vault and creates normal user."""
        response = self.client.post(reverse('accounts:register'), {
            'role': 'user',
            'name': 'Rohan Mehra',
            'email': 'rohan@example.com',
            'password': 'StrongPassword123!',
            'confirm': 'StrongPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('accounts:vault'))
        u = User.objects.get(email='rohan@example.com')
        self.assertFalse(hasattr(u, 'artist_profile'))
        self.assertTrue(hasattr(u, 'collector_profile'))
        self.assertEqual(u.collector_profile.name, 'Rohan Mehra')

    def test_artist_registration(self):
        """Registering as an artist / seller creates an Artist profile and redirects to studio dashboard."""
        response = self.client.post(reverse('accounts:register'), {
            'role': 'artist',
            'name': 'Pooja Verma',
            'email': 'pooja@example.com',
            'password': 'StrongPassword123!',
            'confirm': 'StrongPassword123!',
            'birth_year': '1990',
            'bio': 'Contemporary figurative painter and printmaker.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('artists:dashboard'))
        u = User.objects.get(email='pooja@example.com')
        self.assertTrue(hasattr(u, 'artist_profile'))
        self.assertEqual(u.artist_profile.name, 'Pooja Verma')
        self.assertEqual(u.artist_profile.birth_year, 1990)

    def test_login_as_collector(self):
        """Collector logging in is redirected to My Vault."""
        response = self.client.post(reverse('accounts:login'), {
            'role': 'user',
            'login_id': 'collector@vault.in',
            'password': 'CollectorPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('accounts:vault'))

    def test_login_as_artist(self):
        """Artist logging in is redirected to Artist Studio Dashboard."""
        response = self.client.post(reverse('accounts:login'), {
            'role': 'artist',
            'login_id': 'artist@artvault.in',
            'password': 'ArtistPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('artists:dashboard'))

    def test_collector_cannot_login_as_artist(self):
        """Collector cannot sign in via the Artist tab."""
        response = self.client.post(reverse('accounts:login'), {
            'role': 'artist',
            'login_id': 'collector@vault.in',
            'password': 'CollectorPassword123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Collector / Buyer')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_artist_cannot_login_as_collector(self):
        """Artist cannot sign in via the Collector tab."""
        response = self.client.post(reverse('accounts:login'), {
            'role': 'user',
            'login_id': 'artist@artvault.in',
            'password': 'ArtistPassword123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Artist / Seller')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_dual_account_registration_and_relationship(self):
        """User registers as Collector, then registers as Artist with same email & name; accounts link."""
        # 1. Register as collector
        resp1 = self.client.post(reverse('accounts:register'), {
            'role': 'user',
            'name': 'Priya Singh',
            'email': 'priya@example.com',
            'password': 'Password123!',
            'confirm': 'Password123!'
        })
        self.assertEqual(resp1.status_code, 302)
        self.assertEqual(resp1.url, reverse('accounts:vault'))
        self.client.logout()

        # 2. Register as artist with same email & name
        resp2 = self.client.post(reverse('accounts:register'), {
            'role': 'artist',
            'name': 'Priya Singh',
            'email': 'priya@example.com',
            'password': 'Password123!',
            'confirm': 'Password123!',
            'birth_year': '1988',
            'bio': 'Watercolour specialist.'
        })
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(resp2.url, reverse('artists:dashboard'))
        self.client.logout()

        # Verify both profiles exist and are linked
        u = User.objects.get(email='priya@example.com')
        self.assertTrue(hasattr(u, 'collector_profile'))
        self.assertTrue(hasattr(u, 'artist_profile'))
        self.assertEqual(u.collector_profile.linked_artist, u.artist_profile)
        self.assertEqual(u.artist_profile.linked_collector, u.collector_profile)

        # 3. Can sign in on Artist tab
        login_artist = self.client.post(reverse('accounts:login'), {
            'role': 'artist',
            'login_id': 'priya@example.com',
            'password': 'Password123!'
        })
        self.assertEqual(login_artist.status_code, 302)
        self.assertEqual(login_artist.url, reverse('artists:dashboard'))
        self.client.logout()

        # 4. Can sign in on Collector tab
        login_coll = self.client.post(reverse('accounts:login'), {
            'role': 'user',
            'login_id': 'priya@example.com',
            'password': 'Password123!'
        })
        self.assertEqual(login_coll.status_code, 302)
        self.assertEqual(login_coll.url, reverse('accounts:vault'))

    def test_artist_studio_dashboard_metrics(self):
        """Artist dashboard reflects paintings, orders, and 5% platform commission cut."""
        # Create an acquired order
        order = Order.objects.create(
            painting=self.painting,
            buyer_name='Kavita Roy',
            buyer_email='kavita@collector.in',
            amount=Decimal('100000.00'),
            gallery_fee=Decimal('5000.00'),
            artist_payout=Decimal('95000.00'),
            sale_type='normal',
            fee_percentage=Decimal('5.00'),
            status='paid'
        )
        self.painting.is_sold = True
        self.painting.save()

        self.client.login(username='artist@artvault.in', password='ArtistPassword123!')
        response = self.client.get(reverse('artists:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Devraj Patel')
        self.assertContains(response, 'Gross Artwork Sales')
        self.assertContains(response, 'Gallery Commission')
        self.assertContains(response, 'Net Artist Payout')
        self.assertContains(response, 'Varanasi Ghats at Dawn')

    def test_artist_can_upload_painting(self):
        """Artist can list a new painting into the gallery."""
        self.client.login(username='artist@artvault.in', password='ArtistPassword123!')
        response = self.client.post(reverse('artists:painting_create'), {
            'title': 'Monsoon in Mumbai',
            'year_created': '2024',
            'style': 'Impressionism',
            'materials': 'Acrylic on textured board',
            'dimensions': '80 x 100 cm',
            'estimated_value': '65000.00',
            'story': 'Capturing the melancholic monsoon twilight.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Painting.objects.filter(title='Monsoon in Mumbai', artist=self.artist).exists())

    def test_order_model_auto_calculates_5_and_exhibition_commission(self):
        """5% is charged for normal selling, and 7-8% (default 7.5%) for exhibition auction."""
        # 1. Normal selling: 5% of 50,000 = 2,500
        order = Order.objects.create(
            painting=self.painting,
            buyer_name='Sunil Gupta',
            buyer_email='sunil@gupta.com',
            amount=Decimal('50000.00'),
            razorpay_order_id='order_test_normal_001',
            status='pending'
        )
        self.assertEqual(order.gallery_fee, Decimal('0.00'))
        self.assertEqual(order.artist_payout, Decimal('0.00'))

        order.status = 'paid'
        order.save()

        self.assertEqual(order.fee_percentage, Decimal('5.00'))
        self.assertEqual(order.gallery_fee, Decimal('2500.00'))     # 5% of 50,000
        self.assertEqual(order.artist_payout, Decimal('47500.00')) # 95% of 50,000

        # 2. Exhibition Auction selling: 7.5% of 100,000 = 7,500
        from paintings.models import Exhibition
        exhibition = Exhibition.objects.create(
            title='Royal Salon Auction 2026',
            slug='royal-salon-auction-2026',
            commission_rate=Decimal('7.50'),
            curator_statement='A premiere auction exhibition.'
        )
        exhibition.paintings.add(self.painting)

        auction_order = Order.objects.create(
            painting=self.painting,
            buyer_name='Rohan Sharma',
            buyer_email='rohan@auction.in',
            amount=Decimal('100000.00'),
            razorpay_order_id='order_test_auction_002',
            status='pending'
        )
        auction_order.status = 'paid'
        auction_order.save()

        self.assertEqual(auction_order.sale_type, 'exhibition')
        self.assertEqual(auction_order.fee_percentage, Decimal('7.50')) # 7.5% (in 7-8% bracket)
        self.assertEqual(auction_order.gallery_fee, Decimal('7500.00'))
        self.assertEqual(auction_order.artist_payout, Decimal('92500.00'))

    def test_vault_access(self):
        """Collector can view their saved collection vault."""
        self.client.login(username='collector@vault.in', password='CollectorPassword123!')
        response = self.client.get(reverse('accounts:vault'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Vault')
        self.assertContains(response, 'Ananya')

    def test_toggle_favourite_ajax(self):
        """Collector can toggle favorite artworks in their vault."""
        self.client.login(username='collector@vault.in', password='CollectorPassword123!')
        url = reverse('accounts:toggle_favourite', args=[self.painting.pk])

        # Save
        res1 = self.client.post(url)
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()['status'], 'saved')
        self.assertTrue(Favourite.objects.filter(user=self.collector, painting=self.painting).exists())

        # Remove
        res2 = self.client.post(url)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()['status'], 'removed')
        self.assertFalse(Favourite.objects.filter(user=self.collector, painting=self.painting).exists())
